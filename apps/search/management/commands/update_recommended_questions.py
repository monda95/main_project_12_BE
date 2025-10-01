from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "추천 질문 MV를 최신 검색 로그 기준으로 갱신합니다."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("추천 질문 MV 갱신을 시작합니다...")

        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW recommended_questions_mv;")

        self.stdout.write(self.style.SUCCESS("추천 질문 MV 갱신을 완료했습니다."))
