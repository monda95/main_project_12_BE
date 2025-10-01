from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import SearchLog

User = get_user_model()


@pytest.mark.django_db
class TestSearchFeatures:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        SearchLog.objects.create(user=self.user, query="apple nutrition")
        SearchLog.objects.create(user=self.user, query="banana benefits")
        SearchLog.objects.create(user=self.user, query="apple smoothie recipe")
        SearchLog.objects.create(user=self.user, query="avocado toast")

    def test_autocomplete_with_prefix(self):
        """자동완성: 'app' 접두사로 시작하는 검색어 목록 반환 테스트"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/search/autocomplete/", {"prefix": "app"})
        assert response.status_code == status.HTTP_200_OK
        assert sorted(response.data) == ["apple nutrition", "apple smoothie recipe"]

    def test_autocomplete_no_prefix(self):
        """자동완성: 접두사가 없을 때 빈 목록 반환 테스트"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/search/autocomplete/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_recent_searches_authenticated(self):
        """최근 검색어: 인증된 사용자의 중복 없는 최신 검색어 목록 조회 테스트"""
        # 동일 검색어 추가
        SearchLog.objects.create(user=self.user, query="avocado toast")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/search/recent/")
        assert response.status_code == status.HTTP_200_OK
        # 중복 제거 및 최신순 정렬 확인
        expected = [
            "avocado toast",
            "apple smoothie recipe",
            "banana benefits",
            "apple nutrition",
        ]
        assert response.data == expected

    def test_recent_searches_unauthenticated(self):
        """최근 검색어: 미인증 사용자가 접근 시 401 에러 발생 테스트"""
        response = self.client.get("/api/v1/search/recent/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("apps.search.views.InferenceService.call_gemini_api")
    def test_recommended_searches_calls_gemini(self, mock_call_gemini):
        """추천 질문: Gemini API를 항상 호출하는지 테스트"""
        mock_call_gemini.return_value = {"ai_content": "- 추천 질문 1\n- 추천 질문 2"}
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/search/recommended/")

        assert response.status_code == status.HTTP_200_OK
        # API 응답이 잘 파싱되는지 확인
        assert response.data["results"] == ["추천 질문 1", "추천 질문 2"]
        # call_gemini_api가 마지막 검색어("avocado toast") 기반 프롬프트로 호출되었는지 확인
        mock_call_gemini.assert_called_once()
        prompt_arg = mock_call_gemini.call_args[0][0]
        assert "avocado toast" in prompt_arg

    def test_recommended_searches_no_history(self):
        """추천 질문: 검색 기록이 없는 사용자는 빈 목록을 받는지 테스트"""
        new_user = User.objects.create_user(
            email="new@example.com", password="password123"
        )
        self.client.force_authenticate(user=new_user)
        response = self.client.get("/api/v1/search/recommended/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []
