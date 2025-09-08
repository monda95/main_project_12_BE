FROM python:3.13-slim

# 시스템 패키지 (PostgreSQL client 등)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# uv 설치 (공식 스크립트 이용)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# pyproject.toml + uv.lock 복사
COPY pyproject.toml uv.lock* ./

# 의존성 설치
RUN uv sync --frozen

# 소스 복사
COPY ./backend /app

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
