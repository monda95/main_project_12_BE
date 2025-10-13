from django.urls import path

from . import views

# /api/v1/users/ 경로 하위에 위치
urlpatterns = [
    path("me/", views.UserDetailView.as_view(), name="me"),
    path("me/password/", views.PasswordChangeView.as_view(), name="password_change"),
]
