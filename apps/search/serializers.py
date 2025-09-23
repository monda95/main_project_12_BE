from rest_framework import serializers


class AutocompleteResponseSerializer(serializers.Serializer):
    """
    검색어 자동완성 응답 직렬화
    - 문자열 배열 형태
    """

    results = serializers.ListField(child=serializers.CharField())


class RecentSearchesResponseSerializer(serializers.Serializer):
    """
    최근 검색어 응답 직렬화
    - 문자열 배열 형태
    """

    queries = serializers.ListField(child=serializers.CharField())


class RecommendedSearchesResponseSerializer(serializers.Serializer):
    """
    추천 질문 응답 직렬화
    - AI가 생성한 문자열 배열 형태
    """

    results = serializers.ListField(child=serializers.CharField())
