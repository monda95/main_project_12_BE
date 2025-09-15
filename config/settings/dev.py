from pathlib import Path

from dotenv import load_dotenv

from .base import *

# ✅ base.py 불러오기 전에 환경변수 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env.dev")


DEBUG = True

# DRF 확장
REST_FRAMEWORK = REST_FRAMEWORK.copy()
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# 개발환경 호스트
ALLOWED_HOSTS = ALLOWED_HOSTS or ["*"]
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]
