# apps/users/pages_urls.py
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="main.html"), name="main-page"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login-page"),
    path(
        "signup/", TemplateView.as_view(template_name="signup.html"), name="signup-page"
    ),
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
