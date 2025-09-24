from django.urls import path
from .views import (
    SearchView,
    RecentSearchesView,
    RecommendedSearchesView,
    AutocompleteView,
)

app_name = "search"

urlpatterns = [
    # 메인 검색 (POST /api/v1/search/)
    path("", SearchView.as_view(), name="search"),
    # 파생 리소스
    path("recent/", RecentSearchesView.as_view(), name="recent"),
    path("recommended/", RecommendedSearchesView.as_view(), name="recommended"),
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),
]
