from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InferenceRunViewSet, InferenceView

app_name = "inference"

router = DefaultRouter()
router.register(r"inference-runs", InferenceRunViewSet, basename="inference-run")

urlpatterns = [
    path("", include(router.urls)),
    path("inference/", InferenceView.as_view(), name="inference-create"),
]
