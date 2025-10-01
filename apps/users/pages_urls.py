# apps/users/pages_urls.py
from django.urls import path
from django.views.generic import TemplateView

from apps.conversations.views import ConversationPageView

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
    path("conversation/", ConversationPageView.as_view(), name="conversation-page"),
]
