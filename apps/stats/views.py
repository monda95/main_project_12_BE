from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PopularQuerySerializer, UserStatsSerializer
from apps.users.models import User
from apps.search.models import PopularQuery


@extend_schema(
    tags=["Search & Stats"],
    summary="인기 검색어 조회",
    responses=PopularQuerySerializer(many=True),
)
class PopularSearchesView(APIView):
    """
    인기 검색어 API
    - 사전 집계된 PopularQuery(MV)에서 읽어옴
    - 관리자 대시보드 또는 공개용 통계에 사용
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        popular_queries = PopularQuery.objects.order_by("-count")[:10]
        return Response(list(popular_queries.values("query", "count")))


@extend_schema(
    tags=["Search & Stats"],
    summary="사용자 통계 조회",
    responses=UserStatsSerializer,
)
class UserStatsView(APIView):
    """
    사용자 통계 API (관리자 전용)
    - 총 가입자 수
    - 활성 사용자 수
    - 최근 7일간 일별 신규 가입자 추이
    """

    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()

        seven_days_ago = timezone.now().date() - timedelta(days=7)
        daily_signups = (
            User.objects.filter(created_at__date__gt=seven_days_ago)
            .annotate(date=timezone.localdate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "daily_signups_last_7_days": list(daily_signups),
        }
        return Response(stats)
