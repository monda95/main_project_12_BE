from django.contrib import admin
from .models import SearchLog, PopularQuery, RecommendedQuestion


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "query",
        "normalized_query",
        "result_count",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__email", "query")
    raw_id_fields = ("user",)


@admin.register(PopularQuery)
class PopularQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "cnt", "last_seen")
    readonly_fields = ("query", "cnt", "last_seen")
    ordering = ("-cnt",)
    search_fields = ("query",)


@admin.register(RecommendedQuestion)
class RecommendedQuestionAdmin(admin.ModelAdmin):
    list_display = ("query", "created_at")
    readonly_fields = ("query", "suggestions", "created_at")
