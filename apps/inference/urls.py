from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InferenceRunViewSet

app_name = "inference"

router = DefaultRouter()
# 'inference-runs' 대신 빈 문자열('')을 등록하여 상위 urls.py에서 경로를 온전히 제어
router.register(r"", InferenceRunViewSet, basename="inference-run")

urlpatterns = [
    path("", include(router.urls)),
]
