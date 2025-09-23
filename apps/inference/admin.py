from django.contrib import admin

from .models import InferenceRun


@admin.register(InferenceRun)
class InferenceRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "model",
        "latency_ms",
        "status",
        "created_at",
    )
    list_filter = ("model", "status", "created_at")
    search_fields = ("conversation__title", "model")
    raw_id_fields = ("conversation",)
