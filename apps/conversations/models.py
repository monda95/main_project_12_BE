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
        # 최신 갱신순 목록/검색 성능 향상: (owner, -updated_at) 복합 인덱스
        indexes = [
            models.Index(
                fields=["owner", "-updated_at"], name="idx_conv_owner_updated"
            ),
        ]
        # 기본 정렬: 최신 갱신순
        ordering = ["-updated_at", "-id"]

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
        # 대화별 시간순 페이지네이션 핵심 인덱스
        indexes = [
            models.Index(
                fields=["conversation", "created_at"], name="idx_msg_conv_created"
            ),
        ]
        # 기본 정렬: 시간순 + 동시타임스탬프 안정화용 id
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:30]}"
