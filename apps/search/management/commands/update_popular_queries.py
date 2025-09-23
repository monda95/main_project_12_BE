from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from apps.search.models import SearchLog, PopularQuery


class Command(BaseCommand):
    help = "Aggregates SearchLog data and updates the PopularQuery table."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting to update popular queries...")

        # 1. 기존 인기 검색어 데이터 삭제
        PopularQuery.objects.all().delete()
        self.stdout.write("Old popular queries deleted.")

        # 2. SearchLog에서 새로운 인기 검색어 집계 (상위 100개)
        popular_queries_data = (
            SearchLog.objects.values("query")
            .annotate(count=Count("query"))
            .order_by("-count")[:100]
        )

        # 3. 새로운 객체 리스트 생성
        new_popular_queries = []
        for item in popular_queries_data:
            new_popular_queries.append(
                PopularQuery(query=item["query"], count=item["count"])
            )

        # 4. bulk_create로 한 번에 삽입
        PopularQuery.objects.bulk_create(new_popular_queries)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {len(new_popular_queries)} popular queries."
            )
        )
