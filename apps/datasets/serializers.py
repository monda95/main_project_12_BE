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
    """
    전처리 작업(PreprocessingJob) 목록 조회, 생성, 상세 조회를 위한 시리얼라이저입니다.
    """

    dataset = serializers.PrimaryKeyRelatedField(
        queryset=Dataset.objects.all()
    )  # 데이터셋 ID로 연결

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
        read_only_fields = ["status", "created_at", "started_at", "finished_at"]

    def create(self, validated_data):
        # 전처리 작업 생성 시 status는 'queued'로 시작
        validated_data["status"] = "queued"
        return super().create(validated_data)
