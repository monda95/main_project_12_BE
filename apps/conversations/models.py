from django.conf import settings
from django.db import models


class Conversation(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="소유자",
    )
    title = models.CharField(max_length=200, verbose_name="대화 제목")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 시각")

    class Meta:
        db_table = "conversations"
        verbose_name = "대화"
        verbose_name_plural = "대화 목록"
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"[{self.owner}] {self.title}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "사용자"
        ASSISTANT = "assistant", "어시스턴트"
        SYSTEM = "system", "시스템"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="대화",
    )
    role = models.CharField(max_length=10, choices=Role.choices, verbose_name="역할")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")

    class Meta:
        db_table = "messages"
        verbose_name = "메시지"
        verbose_name_plural = "메시지 목록"
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:30]}"
