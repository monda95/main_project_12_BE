from django.contrib import admin

from .models import InferenceRun


@admin.register(InferenceRun)
class InferenceRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "message",
        "model",
        "latency_ms",
        "status",
        "created_at",
    )
    list_filter = ("model", "status", "created_at")
    search_fields = ("conversation__title", "message__content", "model")
    raw_id_fields = ("conversation", "message")
