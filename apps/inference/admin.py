from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import InferenceRun


@admin.register(InferenceRun)
class InferenceRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "owner_email",  # 소유자 이메일 필드 추가
        "model",
        "latency_ms",
        "status",
        "check_pass",
        "retry_used",
        "created_at",
    )
    list_filter = ("model", "status", "created_at", "check_pass", "retry_used")
    search_fields = (
        "conversation__title",
        "model",
        "conversation__owner__email",  # 소유자 이메일로 검색 추가
    )
    raw_id_fields = ("conversation",)
    readonly_fields = ("created_at",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[InferenceRun]:
        # N+1 문제 방지를 위해 related 객체를 미리 로드
        return (
            super()
            .get_queryset(request)
            .select_related("conversation", "conversation__owner")
        )

    @admin.display(description="소유자 이메일", ordering="conversation__owner__email")
    def owner_email(self, obj: InferenceRun) -> str | None:
        if obj.conversation and obj.conversation.owner:
            return obj.conversation.owner.email
        return "(비회원)"
