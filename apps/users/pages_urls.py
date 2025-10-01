# apps/users/pages_urls.py
import logging

from django.db.utils import OperationalError, ProgrammingError
from django.urls import path
from django.views.generic import TemplateView

from apps.conversations.views import ConversationPageView
from apps.users.views import SignupPageView

from apps.search.models import PopularQuery, RecommendedQuestion


logger = logging.getLogger(__name__)


class MainPageView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recommended_queries = []
        popular_queries = []

        try:
            recommended_queries = list(
                RecommendedQuestion.objects.order_by("-created_at")[:10]
            )
            popular_queries = list(PopularQuery.objects.order_by("-cnt")[:10])
        except (ProgrammingError, OperationalError) as exc:
            logger.warning("추천/인기 검색어 조회 중 오류가 발생했습니다: %s", exc)

        context.update(
            {
                "recommended_queries": recommended_queries,
                "popular_queries": popular_queries,
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
