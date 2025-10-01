# apps/users/pages_urls.py
from django.urls import path
from django.views.generic import TemplateView

from .views import LoginPageView, SignupPageView

urlpatterns = [
    path("", TemplateView.as_view(template_name="main.html"), name="main-page"),
    path("login/", LoginPageView.as_view(), name="login-page"),
    path("signup/", SignupPageView.as_view(), name="signup-page"),
    path(
        "dashboard/",
        TemplateView.as_view(template_name="dashboard.html"),
        name="dashboard-page",
    ),
    path(
        "conversation/",
        TemplateView.as_view(template_name="conversation.html"),
        name="conversation-page",
    ),
]
