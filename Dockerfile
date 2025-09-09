# Python 3.13 slim
FROM python:3.13-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl ca-certificates build-essential libpq-dev git && \
    rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 의존성 먼저 동결 설치(캐시 최적화)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

# 앱 소스
COPY . .

# 실행 스크립트 권한
RUN chmod +x /app/run.sh

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/app/run.sh"]