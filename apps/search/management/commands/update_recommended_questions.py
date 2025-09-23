from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from apps.search.models import SearchLog, RecommendedQuestion
from apps.inference.services import InferenceService  # Gemini API 호출 유틸


class Command(BaseCommand):
    help = "Generates recommended questions for top queries and stores them in the RecommendedQuestions table."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting to update recommended questions...")

        # 1. 최근 검색어 집계 (예: 상위 50개)
        top_queries = (
            SearchLog.objects.values("normalized_query")
            .annotate(count=Count("id"))
            .order_by("-count")[:50]
        )

        new_recommendations = []
        for item in top_queries:
            query = item["normalized_query"]

            # Gemini API 호출 (보정 포함)
            prompt = f"""
            사용자가 '{query}'를 검색함.
            이 주제와 관련하여 추가로 유용할 만한 질문 4개를 한국어로 제안해줘.
            질문은 짧고 자연스럽게.
            """
            suggestions = InferenceService.call_gemini_api(
                prompt, {"max_suggestions": 4}
            ).get("ai_content")

            if suggestions:
                new_recommendations.append(
                    RecommendedQuestion(query=query, suggestions=suggestions)
                )

        # 2. 기존 데이터 삭제 후 새로 삽입
        RecommendedQuestion.objects.all().delete()
        RecommendedQuestion.objects.bulk_create(new_recommendations)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {len(new_recommendations)} recommended questions."
            )
        )
