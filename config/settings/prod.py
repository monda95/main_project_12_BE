from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = [
    "13.125.180.143",
    "ec2-13-125-180-143.ap-northeast-2.compute.amazonaws.com",
    "localhost",
    "127.0.0.1",
    "::1",
]
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

# === MVP 환경 (EC2 HTTP-only) ===
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = None

# CSRF 신뢰 오리진 (HTTP 기준)
CSRF_TRUSTED_ORIGINS = [
    "http://13.125.180.143",
    "http://ec2-13-125-180-143.ap-northeast-2.compute.amazonaws.com",
]
