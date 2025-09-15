from django.contrib import admin

from .models import Dataset, PreprocessingJob


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "source", "created_at")
    list_filter = ("source", "created_at", "owner")
    search_fields = ("name", "owner__email")
    raw_id_fields = ("owner",)


@admin.register(PreprocessingJob)
class PreprocessingJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dataset",
        "status",
        "client_job_id",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "created_at", "started_at", "finished_at")
    search_fields = ("dataset__name", "client_job_id")
    raw_id_fields = ("dataset",)
