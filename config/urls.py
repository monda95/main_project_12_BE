from django.contrib import admin
from django.db import connection
from django.urls import include, path
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter  # DefaultRouter 임포트
from apps.inference.views import InferenceView


@extend_schema(exclude=True)
class HealthzView(APIView):
    """
    Health Check (Liveness Probe)

    애플리케이션이 살아있는지 확인합니다.
    - DB 연결은 확인하지 않고, 단순히 서비스가 살아있는지만 체크합니다.
    - 주로 로드밸런서 또는 쿠버네티스 `livenessProbe`에서 사용합니다.

    응답 예시:
    { "status": "OK" }
    """

    permission_classes = []  # 인증 불필요

    def get(self, request):
        return Response({"status": "OK"}, status=200)


@extend_schema(exclude=True)
class ReadinessView(APIView):
    """
    Readiness Check (Readiness Probe)

    애플리케이션이 요청을 처리할 준비가 되었는지 확인합니다.
    - 내부적으로 데이터베이스 연결 테스트를 수행합니다.
    - DB 연결이 성공하면 `200 OK`, 실패하면 `503 Service Unavailable`을 반환합니다.
    - 주로 쿠버네티스 `readinessProbe`에서 사용합니다.

    성공 응답 예시:
    { "status": "OK" }

    실패 응답 예시:
    { "status": "Service Unavailable" }
    """

    permission_classes = []  # 인증 불필요

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response({"status": "OK"}, status=200)
        except Exception:
            return Response({"status": "Service Unavailable"}, status=503)


# 라우터 생성 및 등록
router_v1 = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Health Check Endpoints
    path("healthz/", HealthzView.as_view(), name="healthz"),
    path("readiness/", ReadinessView.as_view(), name="readiness"),
    # API v1 라우팅
    path("api/v1/auth/", include("apps.users.auth_urls")),  # 인증 관련 API
    path("api/v1/users/", include("apps.users.urls")),  # 사용자 정보 관련 API
    path("api/v1/conversations/", include("apps.conversations.urls")),  # 대화 관련 API
    path("api/v1/inference/", InferenceView.as_view(), name="inference-create"),
    path("api/v1/inference-runs/", include("apps.inference.urls")),
    path("api/v1/search/", include("apps.search.urls")),  # 검색/히스토리 API
    path("api/v1/stats/", include("apps.stats.urls")),  # 통계 API
    path("", include("apps.users.pages_urls")),  # templates URL 매핑
]
