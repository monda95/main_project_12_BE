#!/bin/bash
set -e

echo "🔧 Waiting for Postgres..."
until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT; do
  echo "⏳ Postgres not ready yet..."
  sleep 1
done
echo "✅ Postgres is ready!"

echo "==== Running migrations ===="
uv run python manage.py migrate --noinput

if [ "$DJANGO_ENV" = "production" ]; then
  echo "🚀 Starting Gunicorn (Uvicorn Workers)"
  export DJANGO_SETTINGS_MODULE=config.settings.prod
  uv run gunicorn \
    --bind 0.0.0.0:8000 \
    -k uvicorn.workers.UvicornWorker \
    config.asgi:application
else
  echo "🛠️ Starting Django Development Server"
  export DJANGO_SETTINGS_MODULE=config.settings.dev
  uv run python manage.py runserver 0.0.0.0:8000
fi