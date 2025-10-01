# apps/users/pages_urls.py
from django.urls import path
from django.views.generic import TemplateView

from apps.conversations.views import ConversationPageView
from apps.users.views import SignupPageView

from apps.search.models import PopularQuery, RecommendedQuestion


class MainPageView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "recommended_queries": RecommendedQuestion.objects.order_by("-created_at")[
                    :10
                ],
                "popular_queries": PopularQuery.objects.order_by("-cnt")[:10],
            }
        )
        return context


urlpatterns = [
    path("", MainPageView.as_view(), name="main-page"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login-page"),
    path("signup/", SignupPageView.as_view(), name="signup-page"),
    path(
        "dashboard/",
        TemplateView.as_view(template_name="dashboard.html"),
        name="dashboard-page",
    ),
    path("conversation/", ConversationPageView.as_view(), name="conversation-page"),
]
