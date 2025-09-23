from django.conf import settings
from django.db import models


class SearchLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="사용자",
    )
    query = models.TextField(verbose_name="검색 질의")
    normalized_query = models.TextField(
        blank=True, null=True, verbose_name="정규화된 검색 질의"
    )
    result_count = models.IntegerField(null=True, blank=True, verbose_name="결과 개수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="검색 시각")

    class Meta:
        db_table = "search_logs"
        verbose_name = "검색 로그"
        verbose_name_plural = "검색 로그 목록"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"], name="idx_searchlogs_created_at"),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else "Anonymous"
        return f"[{user_email}] {self.query[:30]}"


class RecommendedQuestion(models.Model):
    query = models.TextField(verbose_name="검색어")
    suggestions = models.JSONField(verbose_name="추천 질문 목록")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")

    class Meta:
        managed = False  # Django가 DDL 관리하지 않음 (MV는 직접 관리)
        db_table = "recommended_questions_mv"
        verbose_name = "추천 질문"
        verbose_name_plural = "추천 질문 목록"
        indexes = [models.Index(fields=["query", "-created_at"])]

    def __str__(self):
        return f"{self.query} ({len(self.suggestions)}개)"


class PopularQuery(models.Model):
    query = models.CharField(max_length=255, unique=True, verbose_name="검색어")
    count = models.PositiveIntegerField(default=0, verbose_name="검색 횟수")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="갱신 시각")

    class Meta:
        managed = False  # Django가 DDL 관리하지 않음 (MV는 직접 관리)
        db_table = "popular_queries_mv"
        verbose_name = "인기 검색어"
        verbose_name_plural = "인기 검색어 목록"
        ordering = ["-count"]

    def __str__(self):
        return f"{self.query} ({self.count}회)"
