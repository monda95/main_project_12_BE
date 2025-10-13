from django.urls import path
from .views import UserStatsView, PopularSearchesView

app_name = "stats"

urlpatterns = [
    path("users/", UserStatsView.as_view(), name="user-stats"),
    path("popular-queries/", PopularSearchesView.as_view(), name="popular-queries"),
]
