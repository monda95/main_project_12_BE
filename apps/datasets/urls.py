from django.urls import path
from .views import PreprocessingJobCreateView

app_name = "datasets"

# 이제 이 파일은 /api/v1/datasets/{pk}/preprocess/ 경로만 담당
urlpatterns = [
    path(
        "<int:dataset_pk>/preprocess/",
        PreprocessingJobCreateView.as_view(),
        name="dataset-preprocess",
    ),
]
