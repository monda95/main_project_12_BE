# === 환경 로딩 ===
import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# === 환경변수 로드 ===
load_dotenv()

# === 경로/플래그 ===
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = (
    os.getenv("DEBUG", "True") == "True"
)  # dev/prod 분기 플래그(운영 보안/렌더러/이메일 등 자동 토글)

# === CORS 개발용: 모든 출처 허용 ===
CORS_ALLOW_ALL_ORIGINS = True

# === 보안 키 ===
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-^kyhex_ex7)0t@+46k#n(8k*n+l51=0ucdy4d^&u=p#_tf(vth",
)

# === 외부 API 키 ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# === 호스트/CSRF ===
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
]
# CSRF_TRUSTED_ORIGINS = [
#     o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
# ]
# ↑ 운영 배포 시 필수: 실제 접근 도메인/오리진을 환경변수로 주입(프록시/도메인 구성에 맞게 갱신)

# === 앱 ===
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # Refresh 회전 후 블랙리스트 적용을 위해 필요
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    # Local apps
    "apps.users",
    "apps.conversations",
    "apps.datasets",
    "apps.inference",
]

# === 미들웨어 ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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

# === ASGI/WSGI ===
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

# === 데이터베이스(PostgreSQL) ===
REQUIRED_VARS = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "NAME": os.getenv("POSTGRES_DB", "fluent"),
        "USER": os.getenv("POSTGRES_USER", "fluent_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "0000"),
        # "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),  # 연결 재사용으로 성능/비용 최적화
    }
}


# === 인증/비밀번호 정책 ===
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
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
    # 개발은 Browsable 허용, 운영은 JSON-only로 자동 전환(↓ DEBUG 분기)
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
    # ↑ 운영에서 UI 렌더러 제거(성능/정보노출 최소화)

# === 스키마/Swagger(drf-spectacular) ===
SPECTACULAR_SETTINGS = {
    "TITLE": "Fluent AI Assistant API",
    "VERSION": "1.0.0",
    "SECURITY": [{"bearerAuth": []}],  # Swagger 전역 보안 스키마(JWT) 선언
    "COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
    "TAGS": [
        {
            "name": "인증/권한",
            "description": "회원가입, 로그인/로그아웃, 토큰 관리 등 사용자 인증 및 권한 관련 API",
        },
        {
            "name": "사용자",
            "description": "내 정보 조회/수정, 탈퇴 등 사용자 정보 관리 API",
        },
        {
            "name": "대화",
            "description": "대화(채팅방) 생성, 조회, 삭제 등 대화 리소스 관리 API",
        },
        {"name": "메시지", "description": "특정 대화에 속한 메시지 생성 및 조회 API"},
        {
            "name": "AI 추론",
            "description": "Gemini AI 모델을 호출하여 추론을 실행하는 API",
        },
        {
            "name": "추론 모니터링",
            "description": "(관리자) AI 추론 실행 기록 모니터링 API",
        },
        {"name": "데이터셋", "description": "(관리자) 학습 데이터셋 리소스 관리 API"},
        {
            "name": "전처리 작업",
            "description": "(관리자) 데이터셋에 대한 전처리 작업 관리 API",
        },
        {"name": "유틸리티", "description": "헬스 체크 등 유틸리티 API"},
    ],
    "SCHEMA_PATH_PREFIX": "/api/v1/",
}

# === 국제화/시간대 ===
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# === 정적/미디어 ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === 기타 ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = True  # url 끝에 / 허용 비허용

# === SimpleJWT ===
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MIN", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,  # 요구사항: Refresh 회전
    "BLACKLIST_AFTER_ROTATION": True,  # 요구사항: 회전 직전 토큰 블랙리스트
}
# ↑ 위 2개 옵션은 token_blacklist 앱까지 활성화되어야 실제 효력

# === 이메일 ===
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
if not DEBUG:
    # 운영에서는 SMTP로 자동 전환(환경변수로 자격증명 주입)
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
    )
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv(
        "DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@example.com"
    )

# === 이메일 인증 강제 플래그 ===
AUTH_EMAIL_VERIFICATION_REQUIRED = (
    os.getenv("AUTH_EMAIL_VERIFICATION_REQUIRED", "False") == "True"
)
# ↑ 요구사항: 운영에서만 True 권장(dev에서는 False). 로그인 뷰에서 이 플래그로 차단.

# === 프록시/HTTPS 보안 ===
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# ↑ Nginx 등 프록시 뒤에서 원본 스킴/호스트를 신뢰하여 HTTPS 인식
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # 운영: HTTP→HTTPS 강제
    SESSION_COOKIE_SECURE = True  # 운영: Secure 쿠키
    CSRF_COOKIE_SECURE = True  # 운영: Secure 쿠키
    CSRF_COOKIE_HTTPONLY = True  # 운영: JS에서 접근 불가
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = int(
        os.getenv("SECURE_HSTS_SECONDS", "31536000")
    )  # 운영: HSTS(기본 1년)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"

# === 로깅(S-프로파일: 콘솔 전용) ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Django 기본 로거 유지
    "handlers": {"console": {"class": "logging.StreamHandler"}},  # 단일 콘솔 핸들러
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },  # 필요 시 수준만 환경변수로 조정
}

# === OAuth2 ===
OAUTH_ALLOWED_PROVIDERS = [
    p.strip()
    for p in os.getenv("OAUTH_ALLOWED_PROVIDERS", "google,github,kakao,naver").split(
        ","
    )
    if p.strip()
]
OAUTH_ALLOW_SIGNUP = (
    os.getenv("OAUTH_ALLOW_SIGNUP", "true").lower() == "true"
)  # 소셜 최초 로그인 시 회원 생성 허용
OAUTH_TRUST_PROVIDER_EMAIL = (
    os.getenv("OAUTH_TRUST_PROVIDER_EMAIL", "true").lower() == "true"
)  # 공급자 email_verified 신뢰

OAUTH_CLIENTS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", ""),
    },
    "kakao": {
        "client_id": os.getenv("KAKAO_CLIENT_ID", ""),
        "client_secret": os.getenv("KAKAO_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("KAKAO_REDIRECT_URI", ""),
    },
    "naver": {
        "client_id": os.getenv("NAVER_CLIENT_ID", ""),
        "client_secret": os.getenv("NAVER_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("NAVER_REDIRECT_URI", ""),
    },
}

# Swagger 제외 경로(브라우저 콜백)
SPECTACULAR_SETTINGS["EXCLUDE_PATHS"] = SPECTACULAR_SETTINGS.get(
    "EXCLUDE_PATHS", []
) + [
    r"^/api/v1/auth/verify/",
]
