from django.db import migrations

# popular_queries_mv 정의
CREATE_MV_SQL = """
CREATE MATERIALIZED VIEW popular_queries_mv AS
SELECT
    normalized_query AS query,
    COUNT(*) AS cnt,
    MAX(created_at) AS last_seen
FROM
    search_logs
GROUP BY
    normalized_query;
"""

# 인덱스 생성
CREATE_INDEX_SQL = """
CREATE UNIQUE INDEX ux_popular_queries_mv_query ON popular_queries_mv (query);
"""

# 뷰 삭제
DROP_MV_SQL = """
DROP MATERIALIZED VIEW IF EXISTS popular_queries_mv;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=f"{CREATE_MV_SQL}{CREATE_INDEX_SQL}",
            reverse_sql=DROP_MV_SQL,
        ),
    ]
