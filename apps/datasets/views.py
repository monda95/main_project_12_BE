from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,  # extend_schema_view 대신 extend_schema 임포트
)
from rest_framework import generics, permissions, viewsets

from .models import Dataset, PreprocessingJob
from .serializers import DatasetSerializer, PreprocessingJobSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    """
    데이터셋(Dataset) 리소스에 대한 CRUD API 뷰셋입니다。
    관리자만 접근 가능합니다。
    """

    queryset = Dataset.objects.all().select_related("owner")
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # 생성 시 요청을 보낸 사용자를 owner로 자동 설정
        serializer.save(owner=self.request.user)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PreprocessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    전처리 작업(PreprocessingJob) 리소스에 대한 조회 API 뷰셋입니다。
    관리자만 접근 가능합니다。
    """

    queryset = PreprocessingJob.objects.all().select_related("dataset")
    serializer_class = PreprocessingJobSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["데이터 전처리"])  # 각 메서드에 추가
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class PreprocessingJobCreateView(generics.CreateAPIView):
    """
    특정 데이터셋에 대한 전처리 작업을 생성하는 API 뷰입니다。
    관리자만 접근 가능합니다。
    """

    serializer_class = PreprocessingJobSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # URL에서 dataset_id를 가져와 해당 데이터셋에 연결
        dataset_id = self.kwargs["dataset_pk"]
        dataset = get_object_or_404(Dataset, id=dataset_id)
        serializer.save(dataset=dataset)

    @extend_schema(tags=["데이터 전처리"])  # 이 데코레이터 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
