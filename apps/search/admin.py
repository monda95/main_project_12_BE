from django.contrib import admin
from .models import SearchLog, PopularQuery, RecommendedQuestion


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "query", "result_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "query")
    raw_id_fields = ("user",)


@admin.register(PopularQuery)
class PopularQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "count", "updated_at")
    ordering = ("-count",)
    readonly_fields = ("query", "count", "updated_at")


@admin.register(RecommendedQuestion)
class RecommendedQuestionAdmin(admin.ModelAdmin):
    list_display = ("query", "created_at")
    readonly_fields = ("query", "suggestions", "created_at")
