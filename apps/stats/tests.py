import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status

from apps.search.models import SearchLog

User = get_user_model()


@pytest.mark.django_db
class TestStatsAPI:
    def setup_method(self):
        self.client = APIClient()
        self.regular_user = User.objects.create_user(
            email="user@example.com", password="password"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )

        # SearchLog를 생성하여 MV 테스트 데이터 기반 마련
        SearchLog.objects.create(normalized_query="apple", query="apple")
        SearchLog.objects.create(normalized_query="apple", query="an apple")
        SearchLog.objects.create(normalized_query="apple", query="apples")
        SearchLog.objects.create(normalized_query="banana", query="banana")
        SearchLog.objects.create(normalized_query="banana", query="a banana")

        # Materialized View 갱신
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW popular_queries_mv")

    def test_popular_queries_accessible_by_anyone(self):
        """인기 검색어 API는 누구나 접근 가능한지 테스트"""
        response = self.client.get("/api/v1/stats/popular-queries/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # ordering = ['-cnt'] 이므로 cnt가 높은 apple이 먼저 와야 함
        assert data[0]["query"] == "apple"
        assert data[0]["cnt"] == 3
        assert data[1]["query"] == "banana"
        assert data[1]["cnt"] == 2

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/v1/stats/popular-queries/")
        assert response.status_code == status.HTTP_200_OK

    def test_user_stats_as_admin_success(self):
        """관리자가 사용자 통계 조회 성공 테스트"""
        # 테스트 데이터 추가
        User.objects.create_user(
            email="inactive@example.com", password="password", is_active=False
        )
        one_day_ago = timezone.now() - timedelta(days=1)

        # auto_now_add 필드를 확실히 재정의하기 위해, 유저 생성 후 날짜를 업데이트합니다.
        new_user = User.objects.create_user(
            email="new1@example.com", password="password"
        )
        new_user.created_at = one_day_ago
        new_user.save(update_fields=["created_at"])

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/v1/stats/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # setup_method 2명 + 현재 테스트 2명
        assert data["total_users"] == 4
        assert data["active_users"] == 3
        assert len(data["daily_signups_last_7_days"]) > 0

        # one_day_ago에 생성된 사용자가 집계에 포함되는지 확인
        signup_counts = {
            item["date"]: item["count"] for item in data["daily_signups_last_7_days"]
        }
        assert signup_counts.get(one_day_ago.strftime("%Y-%m-%d")) == 1

    def test_user_stats_as_regular_user_fails(self):
        """일반 사용자가 사용자 통계 조회 실패 테스트 (403 Forbidden)"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/v1/stats/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_stats_unauthenticated_fails(self):
        """미인증 사용자가 사용자 통계 조회 실패 테스트 (401 Unauthorized)"""
        response = self.client.get("/api/v1/stats/users/")
        # IsAdminUser > IsAuthenticated 이므로 인증되지 않은 요청은 401을 반환
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
