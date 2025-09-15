from django.urls import path

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# ) # 이 줄은 더 이상 필요 없음
from . import views

# /api/v1/auth/ 경로 하위에 위치
urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/", views.CustomTokenObtainPairView.as_view(), name="login"
    ),  # 프록시 뷰 사용
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"
    ),  # 프록시 뷰 사용
]
