from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework import status

from apps.search.models import SearchLog
from apps.inference.services import InferenceService
from apps.inference.serializers import (
    InferenceRequestSerializer,
    InferenceResponseSerializer,
)
from .serializers import (
    AutocompleteResponseSerializer,
    RecommendedSearchesResponseSerializer,
)


@extend_schema(
    tags=["Search & Stats"],
    summary="범용 검색 (Inference 위임)",
    request=InferenceRequestSerializer,
    responses=InferenceResponseSerializer,
)
class SearchView(APIView):
    """
    사용자의 검색 요청(prompt)을 받아 InferenceService를 통해 AI 추론을 실행합니다.
    이 API는 사실상 InferenceView의 프록시(대리인) 역할을 수행하며,
    Self-Check, 로깅, 재시도 등 모든 핵심 로직을 재사용합니다.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        req_ser = InferenceRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        result = InferenceService.run_inference(
            conversation_id=req_ser.validated_data.get("conversation_id"),
            prompt=req_ser.validated_data["prompt"],
            user=request.user,
            options=req_ser.validated_data.get("options", {}),
        )

        if result.get("status") == "error":
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)

        out_ser = InferenceResponseSerializer(result)
        return Response(out_ser.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Search & Stats"],
    summary="검색어 자동완성",
    responses=AutocompleteResponseSerializer,
)
class AutocompleteView(APIView):
    """
    검색어 자동완성 API
    - `?prefix=...` 쿼리 파라미터를 받아, 해당 문자열로 시작하는 기존 검색어를 추천합니다.
    - 사용자 검색 로그(SearchLog)를 직접 조회하여 제안합니다.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        prefix = request.query_params.get("prefix", "").strip()
        if not prefix:
            return Response([])

        # 소문자로 일치하는 검색어 조회 후 중복 제거 및 10개 제한
        suggestions = (
            SearchLog.objects.filter(query__istartswith=prefix)
            .values_list("query", flat=True)
            .distinct()
            .order_by("query")[:10]
        )
        return Response(list(suggestions))


@extend_schema(
    tags=["Search & Stats"],
    summary="최근 검색어 목록",
    responses=RecommendedSearchesResponseSerializer,
)
class RecentSearchesView(ListAPIView):
    """
    현재 로그인한 사용자의 최근 검색 기록을 반환합니다.
    - 동일 검색어는 중복 제거
    - 최대 20개까지만 반환
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None  # 직렬화는 Response에서 직접 처리

    def get_queryset(self):
        return SearchLog.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        seen, unique_queries = set(), []
        for log in self.get_queryset():
            if log.query not in seen:
                seen.add(log.query)
                unique_queries.append(log.query)
        return Response(unique_queries[:20])


@extend_schema(
    tags=["Search & Stats"],
    summary="추천 질문 생성",
    responses=RecommendedSearchesResponseSerializer,
)
class RecommendedSearchesView(APIView):
    """
    최근 검색어 기반 추천 질문 API
    - DB 캐시(RecommendedQuestion 모델)는 사용하지 않고, 최근 검색어 → Gemini API 직통 호출
    - 추천 질문은 Gemini가 생성하며, 최대 4개까지 반환
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1) 최근 검색어 확인
        last_log = (
            SearchLog.objects.filter(user=request.user).order_by("-created_at").first()
        )
        if not last_log:
            return Response({"results": []})

        query = last_log.query.strip()

        # 2) Gemini API 프롬프트 정의
        prompt = f"""
        사용자가 '{query}'를 검색했습니다.
        이 주제와 관련하여 추가로 유용할 만한 질문 4개를 한국어로 제안해주세요.
        질문은 짧고 자연스럽게 작성해 주세요.
        """

        # 3) Gemini API 호출 (Self-Check 불필요 → 단순 호출)
        gemini_result = InferenceService.call_gemini_api(
            prompt, {"maxOutputTokens": 128}
        )
        ai_output = gemini_result.get("ai_content", "")

        # 4) 응답 후처리: 줄바꿈/불필요 문자 제거
        suggestions = ai_output.split("\n")
        suggestions = [s.strip("- ").strip() for s in suggestions if s.strip()]

        return Response({"results": suggestions[:4]})
