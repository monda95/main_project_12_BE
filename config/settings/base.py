# ============================================
# Django Base Settings (HTTP-only / EC2 배포용)
# ============================================

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# === 환경 로딩 ===
load_dotenv()

# === 경로/플래그 ===
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = os.getenv("DEBUG", "True") == "True"

# === CORS ===
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True  # Swagger 등에서 CSRF 오류 방지

# === 보안 키 ===
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-^kyhex_ex7)0t@+46k#n(8k*n+l51=0ucdy4d^&u=p#_tf(vth",
)

# === 외부 API ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

# === 호스트 ===
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
]

# === 앱 ===
INSTALLED_APPS = [
    # Django 기본
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "django_celery_beat",
    # Local apps
    "apps.users",
    "apps.conversations",
    "apps.inference",
    "apps.search",
    "apps.stats",
]

# === 미들웨어 ===
MIDDLEWARE = [
    "apps.core.middleware.ForceHttpSchemeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.DisableHSTSMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# === URL 루트 ===
ROOT_URLCONF = "config.urls"

# === 템플릿 ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === ASGI/WSGI ===
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

# === 데이터베이스(PostgreSQL) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "NAME": os.getenv("POSTGRES_DB", "fluent"),
        "USER": os.getenv("POSTGRES_USER", "fluent_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "0000"),
    }
}

# === 인증/비밀번호 정책 ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "users.User"

# === DRF 공통 ===
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
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("API_PAGE_SIZE", "20")),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_RATE_ANON", "20/min"),
        "user": os.getenv("THROTTLE_RATE_USER", "60/min"),
    },
}
if not DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer"
    ]

# === Swagger / drf-spectacular ===
SPECTACULAR_SETTINGS = {
    "TITLE": "Smart Nourish Assistant API",
    "DESCRIPTION": "음식·영양 정보 특화 AI 가상비서 API 문서",
    "VERSION": "1.0.0",
    "SECURITY": [{"bearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}

# === 국제화/시간대 ===
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# === 정적/미디어 ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === 기타 ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = True

# === SimpleJWT ===
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MIN", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# === 이메일 ===
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
if not DEBUG:
    EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv(
        "DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@example.com"
    )

# === OAuth2 설정 ===
OAUTH_ALLOWED_PROVIDERS = [
    p.strip()
    for p in os.getenv("OAUTH_ALLOWED_PROVIDERS", "github").split(",")
    if p.strip()
]
OAUTH_ALLOW_SIGNUP = os.getenv("OAUTH_ALLOW_SIGNUP", "true").lower() == "true"
OAUTH_TRUST_PROVIDER_EMAIL = os.getenv("OAUTH_TRUST_PROVIDER_EMAIL", "true").lower() == "true"
OAUTH_CLIENTS = {
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", ""),
    },
}

# ==================================================
# ✅ HTTP-only 안전 배포용 보안 설정 (HTTPS 오인 완전 차단)
# ==================================================
USE_X_FORWARDED_HOST = False
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = "SAMEORIGIN"

CSRF_TRUSTED_ORIGINS = [
    "http://13.125.180.143",
    "http://localhost",
    "http://127.0.0.1",
]

# === 로깅 ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "apps.inference.services": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
        "django.request": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
