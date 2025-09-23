from django.urls import path
from .views import (
    RecentSearchesView,
    RecommendedSearchesView,
    AutocompleteView,
)

app_name = "search"

urlpatterns = [
    path("recent/", RecentSearchesView.as_view(), name="recent-searches"),
    path(
        "recommended/", RecommendedSearchesView.as_view(), name="recommended-searches"
    ),
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete-searches"),
]
