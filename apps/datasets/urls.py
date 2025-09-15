from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DatasetViewSet, PreprocessingJobCreateView, PreprocessingJobViewSet

app_name = "datasets"

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")
router.register(
    r"preprocessing-jobs", PreprocessingJobViewSet, basename="preprocessing-job"
)

urlpatterns = [
    path("", include(router.urls)),
    # 중첩된 전처리 작업 생성 URL: /api/v1/datasets/{dataset_pk}/preprocess/
    path(
        "datasets/<int:dataset_pk>/preprocess/",
        PreprocessingJobCreateView.as_view(),
        name="dataset-preprocess",
    ),
]
