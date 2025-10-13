# Python 3.13 slim
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential libpq-dev git postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 의존성 먼저(캐시 최적화)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

# 앱 소스
COPY . .

# CRLF 방지 + 실행권한 (루트에 scripts/run.sh가 있다고 가정)
RUN sed -i 's/\r$//' scripts/run.sh && chmod +x scripts/run.sh

EXPOSE 8000

# 실행 비트가 혹시 바인드 마운트로 사라져도 동작하도록 sh로 실행
ENTRYPOINT ["/bin/sh","-lc","sh scripts/run.sh"]

# 도커이미지 만들기
# docker build -t django-financial .

# 멈추고 지운 다음 다시 생성 + 시작하기
# docker stop django-financial
# docker rm django-financial
# docker run -d -p 8000:8000 --name django-financial django-financial
