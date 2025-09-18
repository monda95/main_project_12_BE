from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import generics, permissions, viewsets

from .models import Dataset, PreprocessingJob
from .serializers import DatasetSerializer, PreprocessingJobSerializer


@extend_schema_view(
    list=extend_schema(summary="[목록] 데이터셋 목록 조회", tags=["데이터셋"]),
    create=extend_schema(summary="[생성] 새 데이터셋 생성", tags=["데이터셋"]),
    retrieve=extend_schema(summary="[조회] 특정 데이터셋 상세 조회", tags=["데이터셋"]),
    update=extend_schema(summary="[수정] 특정 데이터셋 수정", tags=["데이터셋"]),
    partial_update=extend_schema(
        summary="[부분 수정] 특정 데이터셋 부분 수정", tags=["데이터셋"]
    ),
    destroy=extend_schema(summary="[삭제] 특정 데이터셋 삭제", tags=["데이터셋"]),
)
class DatasetViewSet(viewsets.ModelViewSet):
    """
    데이터셋(Dataset) 리소스에 대한 CRUD API 뷰셋입니다.

    **권한**: 관리자만 접근 가능합니다.
    """

    queryset = Dataset.objects.all().select_related("owner")
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "post", "patch", "delete"]  # PUT 제외

    def perform_create(self, serializer):
        # 생성 시 요청을 보낸 사용자를 owner로 자동 설정
        serializer.save(owner=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="[목록] 전처리 작업 목록 조회", tags=["전처리 작업"]),
    retrieve=extend_schema(
        summary="[조회] 특정 전처리 작업 상세 조회", tags=["전처리 작업"]
    ),
)
class PreprocessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    전처리 작업(PreprocessingJob) 리소스에 대한 조회 API 뷰셋입니다.

    **권한**: 관리자만 접근 가능합니다.
    """

    queryset = PreprocessingJob.objects.all().select_related("dataset")
    serializer_class = PreprocessingJobSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(summary="[생성] 새 전처리 작업 생성", tags=["전처리 작업"])
class PreprocessingJobCreateView(generics.CreateAPIView):
    """
    특정 데이터셋에 대한 전처리 작업을 생성하는 API 뷰입니다.

    URL의 `dataset_pk`를 통해 대상 데이터셋이 지정됩니다.

    **권한**: 관리자만 접근 가능합니다.
    """

    serializer_class = PreprocessingJobSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # URL에서 dataset_id를 가져와 해당 데이터셋에 연결
        dataset_id = self.kwargs["dataset_pk"]
        dataset = get_object_or_404(Dataset, id=dataset_id)
        serializer.save(dataset=dataset)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
