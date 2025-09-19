from rest_framework import serializers
from .models import Dataset, PreprocessingJob


class DatasetSerializer(serializers.ModelSerializer):
    """
    데이터셋(Dataset) 목록 조회, 생성, 수정, 상세 조회를 위한 시리얼라이저입니다.
    """

    owner = serializers.ReadOnlyField(source="owner.email")  # 소유자 이메일 표시

    class Meta:
        model = Dataset
        fields = ["id", "owner", "name", "source", "uri", "created_at"]
        read_only_fields = ["owner", "created_at"]

    def create(self, validated_data):
        # 생성 시 요청을 보낸 사용자를 owner로 자동 설정
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class PreprocessingJobSerializer(serializers.ModelSerializer):
    # dataset은 URL 경로로만 지정되며, 입력(body)에서는 받지 않음
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PreprocessingJob
        fields = [
            "id",
            "dataset",
            "client_job_id",
            "status",
            "steps",
            "created_at",
            "started_at",
            "finished_at",
        ]
        read_only_fields = [
            "dataset",
            "client_job_id",
            "status",
            "created_at",
            "started_at",
            "finished_at",
        ]

    def create(self, validated_data):
        dataset = validated_data.get("dataset")
        owner = dataset.owner if dataset else None
        steps = validated_data.get("steps") or {}  # None/빈값 안전 처리

        # 멱등키 자동 생성
        validated_data["client_job_id"] = PreprocessingJob.generate_client_job_id(
            dataset.id if dataset else None,
            owner.id if owner else None,
            steps,
        )
        # 기본 상태는 queued
        validated_data["status"] = PreprocessingJob.Status.QUEUED
        return super().create(validated_data)
