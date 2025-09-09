from . import base as base_settings

DEBUG = True

REST_FRAMEWORK = base_settings.REST_FRAMEWORK.copy()
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

ALLOWED_HOSTS = base_settings.ALLOWED_HOSTS or ["*"]
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]
