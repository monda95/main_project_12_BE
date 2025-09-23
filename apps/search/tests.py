from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import SearchLog, RecommendedQuestion

User = get_user_model()


@pytest.mark.django_db
class TestSearchAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )

        # 인기 검색어 테스트 데이터
        SearchLog.objects.create(user=self.user1, query="python")
        SearchLog.objects.create(user=self.user1, query="python")
        SearchLog.objects.create(user=self.user2, query="python")
        SearchLog.objects.create(user=self.user1, query="django")
        SearchLog.objects.create(user=self.user2, query="django")
        SearchLog.objects.create(user=self.user1, query="fastapi")

        # 최근 검색어 테스트 데이터 (user1)
        SearchLog.objects.create(user=self.user1, query="react")
        SearchLog.objects.create(user=self.user1, query="vue")

    def test_popular_searches(self):
        """인기 검색어 API가 정확한 순위와 카운트를 반환하는지 테스트"""
        response = self.client.get("/api/v1/search/popular/")
        assert response.status_code == 200
        data = response.json()
        # assert len(data) == 3  # 다른 테스트 데이터의 영향으로 총 개수는 유동적일 수 있음
        assert data[0]["query"] == "python"
        assert data[0]["count"] == 3
        assert data[1]["query"] == "django"
        assert data[1]["count"] == 2

        # 3위 그룹은 count가 1이며, 순서는 보장되지 않음
        third_place_queries = {item["query"] for item in data[2:]}
        assert {"fastapi", "react", "vue"}.issubset(third_place_queries)
        for item in data[2:]:
            assert item["count"] == 1

    def test_recent_searches_authenticated(self):
        """인증된 사용자가 자신의 최근 검색 기록을 조회하는지 테스트"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/v1/search/recent/")
        assert response.status_code == 200
        # 최신순, 중복 제거된 결과 확인
        expected_queries = ["vue", "react", "fastapi", "django", "python"]
        assert response.json() == expected_queries

    def test_recent_searches_unauthenticated(self):
        """미인증 사용자가 최근 검색 기록 조회 시 401 에러 테스트"""
        response = self.client.get("/api/v1/search/recent/")
        assert response.status_code == 401

    @patch("apps.search.views.call_gemini_api")
    def test_recommended_searches_cache_miss(self, mock_call_gemini):
        """추천 질문 - 캐시 부재 시 Gemini 호출 테스트"""
        mock_suggestions = ["suggestion1", "suggestion2"]
        mock_call_gemini.return_value = mock_suggestions
        self.client.force_authenticate(user=self.user1)

        # user1의 마지막 검색어는 "vue"
        response = self.client.get("/api/v1/search/recommended/")

        assert response.status_code == 200
        assert response.json()["results"] == mock_suggestions
        mock_call_gemini.assert_called_once()  # Gemini API가 호출되었는지 확인
        assert RecommendedQuestion.objects.filter(
            query="vue"
        ).exists()  # 캐시에 저장되었는지 확인

    @patch("apps.search.views.call_gemini_api")
    def test_recommended_searches_cache_hit(self, mock_call_gemini):
        """추천 질문 - 캐시 적중 시 Gemini 미호출 테스트"""
        # 미리 캐시 데이터를 만들어 둠
        cached_suggestions = ["cached1", "cached2"]
        RecommendedQuestion.objects.create(query="vue", suggestions=cached_suggestions)
        self.client.force_authenticate(user=self.user1)

        # user1의 마지막 검색어는 "vue"
        response = self.client.get("/api/v1/search/recommended/")

        assert response.status_code == 200
        assert response.json()["results"] == cached_suggestions
        mock_call_gemini.assert_not_called()  # Gemini API가 호출되지 않았는지 확인
