from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0003_alter_popularquery_options_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW popular_queries_mv AS
            SELECT query, COUNT(*) AS count, MAX(created_at) AS last_seen
            FROM search_logs
            GROUP BY query
            ORDER BY count DESC;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS popular_queries_mv;",
        ),
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW recommended_questions_mv AS
            SELECT query, json_agg(DISTINCT normalized_query) AS suggestions, NOW() AS created_at
            FROM search_logs
            GROUP BY query;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS recommended_questions_mv;",
        ),
    ]
