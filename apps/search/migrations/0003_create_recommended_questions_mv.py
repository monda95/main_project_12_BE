from django.db import migrations


CREATE_MV_SQL = """
CREATE MATERIALIZED VIEW recommended_questions_mv AS
WITH deduped AS (
    SELECT
        normalized_query,
        query,
        MAX(created_at) AS last_seen
    FROM
        search_logs
    WHERE
        normalized_query IS NOT NULL
    GROUP BY
        normalized_query,
        query
),
ranked AS (
    SELECT
        normalized_query,
        query,
        last_seen,
        ROW_NUMBER() OVER (
            PARTITION BY normalized_query
            ORDER BY last_seen DESC
        ) AS rn
    FROM
        deduped
)
SELECT
    normalized_query AS query,
    jsonb_agg(query ORDER BY last_seen DESC) AS suggestions,
    timezone('UTC', now()) AS created_at
FROM
    ranked
WHERE
    rn <= 4
GROUP BY
    normalized_query;
"""


CREATE_INDEX_SQL = """
CREATE INDEX idx_recommended_questions_mv_query_created_at
    ON recommended_questions_mv (query, created_at DESC);
"""


DROP_OBJECTS_SQL = """
DROP INDEX IF EXISTS idx_recommended_questions_mv_query_created_at;
DROP MATERIALIZED VIEW IF EXISTS recommended_questions_mv;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0002_create_popular_queries_mv"),
    ]

    operations = [
        migrations.RunSQL(
            sql=f"{CREATE_MV_SQL}{CREATE_INDEX_SQL}",
            reverse_sql=DROP_OBJECTS_SQL,
        ),
    ]
