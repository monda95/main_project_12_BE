# from celery import shared_task
# from django.db import connection
#
# @shared_task
# def refresh_popular_queries_mv():
#     with connection.cursor() as cur:
#         # 동시 읽기 차단 최소화를 위해 CONCURRENTLY 사용
#         cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY popular_queries_mv;")
