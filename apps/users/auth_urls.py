from django.urls import path
from . import views

# /api/v1/auth/ 경로 하위에 위치
urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "login/", views.CustomTokenObtainPairView.as_view(), name="login"
    ),  # 프록시 뷰 사용
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path(
        "verify/<uidb64>/<token>/", views.verify_email, name="verify_email"
    ),  # 프록시 뷰 사용
]
