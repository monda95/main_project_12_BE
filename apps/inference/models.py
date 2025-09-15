from django.db import models


class InferenceRun(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "성공"
        ERROR = "error", "오류"

    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.CASCADE,
        related_name="inference_runs",
        verbose_name="대화",
    )
    message = models.ForeignKey(
        "conversations.Message",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inference_runs",
        verbose_name="관련 메시지",
    )
    model = models.CharField(max_length=50, verbose_name="사용 모델")
    latency_ms = models.IntegerField(verbose_name="지연 시간(ms)")
    prompt_tokens = models.IntegerField(
        null=True, blank=True, verbose_name="프롬프트 토큰 수"
    )
    completion_tokens = models.IntegerField(
        null=True, blank=True, verbose_name="응답 토큰 수"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUCCESS,
        verbose_name="상태",
    )
    error_code = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="오류 코드"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")

    class Meta:
        db_table = "inference_runs"
        verbose_name = "추론 실행"
        verbose_name_plural = "추론 실행 목록"
        indexes = [
            models.Index(fields=["conversation"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.model} in {self.latency_ms}ms"
