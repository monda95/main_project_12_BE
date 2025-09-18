from django.contrib import admin

from .models import Dataset, PreprocessingJob


class PreprocessingJobInline(admin.TabularInline):
    model = PreprocessingJob
    # 인라인 뷰에서 보여줄 필드들을 지정합니다.
    fields = (
        "id",
        "status",
        "client_job_id",
        "created_at",
        "started_at",
        "finished_at",
    )
    # 인라인 뷰에서는 모든 필드를 읽기 전용으로 설정하여, 상태 확인만 가능하게 합니다.
    readonly_fields = fields
    # 인라인 뷰를 통해 새 작업을 추가하는 것을 비활성화합니다.
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "source", "created_at")
    list_filter = ("source", "created_at", "owner")
    search_fields = ("name", "owner__email")
    raw_id_fields = ("owner",)
    # Dataset 관리자 페이지에 PreprocessingJob 인라인을 추가합니다.
    inlines = [PreprocessingJobInline]


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
