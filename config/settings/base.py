import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = os.getenv("DEBUG", "True") == "True"

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-^kyhex_ex7)0t@+46k#n(8k*n+l51=0ucdy4d^&u=p#_tf(vth",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
] or ["*"]
# CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()] 배포할 때 꼭 활성화해서 작동시켜야 함


# Application definition

INSTALLED_APPS = [
    # 기본 Django 앱
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party 앱
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    # 로컬 앱
    "apps.users",
    "apps.conversations",
    "apps.datasets",
    "apps.inference",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# run.sh에서 UvicornWorker로 ASGI를 띄우므로 ASGI_APPLICATION을 명시
ASGI_APPLICATION = "config.asgi.application"
# (선택) 관리 명령 등 WSGI 경로가 필요하면 유지
WSGI_APPLICATION = "config.wsgi.application"

# ── Database: Postgres_* 환경변수만 사용 (SQLite/DATABASE_URL 없음)
REQUIRED_VARS = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]
missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Missing required DB envs: {', '.join(missing)}")
#
# 📌 기능 설명
# 필수 환경변수 목록 정의
# REQUIRED_VARS 안에 PostgreSQL 연결에 꼭 필요한 값들을 넣습니다.
# os.getenv()로 값 확인
# .env에서 불러온 환경변수들을 하나씩 확인.
# 값이 비어 있으면 missing 리스트에 추가.

# 누락 시 예외 발생
#
# 만약 누락된 값이 있다면 RuntimeError를 발생시켜 Django 실행을 멈춥니다
# 예: POSTGRES_PASSWORD가 없으면 바로 에러 → python manage.py runserver나 docker-compose up 할 때 중단됨.

# 📌 왜 쓰는가?
# 안전성 확보: DB 연결 정보가 누락된 상태로 잘못 실행되는 걸 막습니다.
# 운영 환경에서 중요:
# EC2나 CI/CD에서 .env 누락 시 SQLite로 fallback 되거나 빈값으로 연결되면 큰 문제 발생.
# 이 가드를 두면 **"DB 환경변수 없어 → 바로 에러"**로 빠르게 원인 파악 가능.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "NAME": os.getenv("POSTGRES_DB", "fluent"),
        "USER": os.getenv("POSTGRES_USER", "fluent_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "0000"),
        "CONN_MAX_AGE": 0,  # 커넥션 재사용 -> 성능 최적화 및 비용 줄일 용도 = "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "600")),
        # "ATOMIC_REQUESTS": True,                                   # 요청 단위 트랜잭션 -> HTTP 요청을 DB트랜잭션으로 감싸게하기 짧은 응답에 유리하지만 장시간 실행되는 View에서 불리한 기능
        # "OPTIONS": {"sslmode": "require"}  # 매니지드 DB/TLS 필요 시 사용
    }
}

# ── Auth validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── DRF
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # dev에서는 BrowsableRenderer 허용, prod에서는 dev/prod 분리 파일에서 조정 권장
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "20/min", "user": "60/min"},
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Fluent AI Assistant API",
    "VERSION": "1.0.0",
    # 전역 보안 요구사항을 Bearer로 고정(선택)
    "SECURITY": [{"bearerAuth": []}],
    # 보안 스키마를 명시적으로 선언(선택: 자동 생성에 맡겨도 됨)
    "COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
    "TAGS": [
        {"name": "인증/권한", "description": "사용자 인증 및 권한 관련 API"},
        {"name": "사용자", "description": "사용자 정보 관리 API"},
        {"name": "대화/메시지", "description": "대화 및 메시지 관리 API"},
        {"name": "태그", "description": "태그 관리 API"},
        {"name": "AI 추론", "description": "Gemini AI 모델 호출 API"},
        {"name": "데이터 전처리", "description": "데이터셋 및 전처리 작업 관리 API"},
        {"name": "추론 모니터링", "description": "AI 추론 기록 모니터링 API"},
        {"name": "유틸리티", "description": "헬스 체크 등 유틸리티 API"},
    ],
    # API 경로 접두사를 설정하여 drf-spectacular가 태그를 더 잘 인식하도록
    "SCHEMA_PATH_PREFIX": "/api/v1/",
}

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

AUTH_USER_MODEL = "users.User"
