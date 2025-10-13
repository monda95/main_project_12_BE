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

echo "🔑 Setting directory permissions..."
STATIC_DIR=/app/staticfiles
MEDIA_DIR=/app/media
APP_DIR=/app

# nginx와 Django 모두 접근 가능하도록 권한 정리
sudo chown -R ubuntu:ubuntu $STATIC_DIR $MEDIA_DIR || true
sudo chmod -R 755 $STATIC_DIR $MEDIA_DIR || true

# 상위 디렉터리 접근권한 확보 (거의 모든 경로 접근 허용)
sudo chmod o+x /home/ubuntu || true
sudo chmod o+rx $APP_DIR || true
sudo chmod -R o+rX $APP_DIR/* || true


if [ "$DJANGO_ENV" = "production" ]; then
  echo "🚀 Starting Gunicorn (Uvicorn Workers)"
  export DJANGO_SETTINGS_MODULE=config.settings.prod
  uv run gunicorn \
    --bind 0.0.0.0:8000 \
    -k uvicorn.workers.UvicornWorker \
    --workers=2 \
    config.asgi:application
# worker의 개수는 구니콘 공식문서 기준 (2 × CPU 코어 수) + 1 이지만 t2.micro를 믿을 수 없어서 2개로 하향조정


# compose.yml 대신에 run.sh로 관리하는
# t2.micro 환경에서 web 컨테이너 안에 gunicorn + celery worker/beat를 subprocess로 통합 실행
#
#  # Celery Worker 실행 (concurrency=1)
#  uv run celery -A config worker -l info --concurrency=1 &
#
#  # Celery Beat 실행 (포그라운드)
#  uv run celery -A config beat -l info \
#    --scheduler django_celery_beat.schedulers:DatabaseScheduler

else
  echo "🛠️ Starting Django Development Server"
  export DJANGO_SETTINGS_MODULE=config.settings.dev
  uv run python manage.py runserver 0.0.0.0:8000
fi
