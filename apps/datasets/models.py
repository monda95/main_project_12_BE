from django.conf import settings
from django.db import models


class Dataset(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="datasets",
        verbose_name="소유자",
    )
    name = models.CharField(max_length=100, verbose_name="데이터셋명")
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
        max_length=64, null=True, blank=True, verbose_name="클라이언트 제공 ID (멱등키)"
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
            models.UniqueConstraint(
                fields=["dataset", "client_job_id"],
                condition=models.Q(client_job_id__isnull=False),
                name="uq_dataset_client_job_id",
            )
        ]
        indexes = [
            models.Index(fields=["dataset"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Job {self.id} for {self.dataset.name} ({self.status})"
