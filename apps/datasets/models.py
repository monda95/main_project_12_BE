import hashlib
import json

from django.conf import settings
from django.db import models


class Dataset(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="datasets",
        verbose_name="소유자",
    )
    name = models.CharField(max_length=100, verbose_name="데이터셋 이름")
    source = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="데이터 원천"
    )
    uri = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="원본 위치(URI)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")

    class Meta:
        db_table = "datasets"
        verbose_name = "데이터셋"
        verbose_name_plural = "데이터셋 목록"
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"], name="idx_datasets_created"),
        ]

    def __str__(self):
        return self.name


class PreprocessingJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "대기"
        RUNNING = "running", "실행 중"
        SUCCEEDED = "succeeded", "성공"
        FAILED = "failed", "실패"

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="preprocessing_jobs",
        verbose_name="데이터셋",
    )
    client_job_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="요청 기반 해시 ID(자동생성 멱등키)",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        verbose_name="상태",
    )
    steps = models.JSONField(null=True, blank=True, verbose_name="전처리 단계")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="시작 시각")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="종료 시각")

    class Meta:
        db_table = "preprocessing_jobs"
        verbose_name = "전처리 작업"
        verbose_name_plural = "전처리 작업 목록"
        constraints = [
            # client_job_id 가 NULL이 아닐 때만 (dataset, client_job_id) 유니크
            models.UniqueConstraint(
                fields=["dataset", "client_job_id"],
                condition=models.Q(client_job_id__isnull=False),
                name="uq_dataset_client_job_id",
            )
        ]
        indexes = [
            models.Index(fields=["dataset"]),
            models.Index(
                fields=["status", "created_at"], name="idx_prejobs_status_created"
            ),
        ]

    def __str__(self):
        return f"Job {self.id} for {self.dataset.name} ({self.status})"

    @staticmethod
    def generate_client_job_id(dataset_id, owner_id, steps):
        """요청 Body + dataset_id + owner_id 기반 멱등키 해시 생성"""
        norm_steps = steps or {}
        raw = json.dumps(
            {
                "dataset_id": dataset_id,
                "owner_id": owner_id,
                "steps": norm_steps,
            },
            sort_keys=True,  # 키 순서 정규화
            separators=(",", ":"),  # 공백 제거 → 안정적 직렬화
        )
        return hashlib.sha256(raw.encode()).hexdigest()  # 64자 hex
