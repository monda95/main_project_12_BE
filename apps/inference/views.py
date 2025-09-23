from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InferenceRun
from .serializers import (
    InferenceRequestSerializer,
    InferenceResponseSerializer,
    InferenceRunSerializer,
)
from apps.inference.services import InferenceService


@extend_schema(
    tags=["AI Inference"],
    summary="Gemini 추론 호출",
    request=InferenceRequestSerializer,
    responses=InferenceResponseSerializer,
)
class InferenceView(APIView):
    """
    Gemini API를 호출하여 AI 추론을 실행하고 관련 데이터를 저장합니다.

    처리 흐름:
    1. 요청 데이터 검증 (conversation_id, prompt, options)
    2. InferenceService.run_inference 실행
       - 대화 조회/생성
       - SearchLog 기록
       - Message 저장
       - Gemini API 호출 및 에러 처리
       - InferenceRun 저장
    3. Gemini 호출 실패 시 → 502 Bad Gateway + 에러 상세 반환
    4. 성공 시 → message_id, role, content, usage 토큰 정보 반환
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        # 1. 요청 검증
        req_ser = InferenceRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 2. 서비스 실행
        result = InferenceService.run_inference(
            conversation_id=req_ser.validated_data.get("conversation_id"),
            prompt=req_ser.validated_data["prompt"],
            user=request.user,
            options=req_ser.validated_data.get("options", {}),
        )

        # 3. 에러 여부 분기
        if result.get("status") == "error":
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)

        # 4. 정상 응답
        out_ser = InferenceResponseSerializer(result)
        return Response(out_ser.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        tags=["AI Inference"],
        summary="추론 실행 기록 목록 조회",
        responses=InferenceRunSerializer(many=True),
    ),
    retrieve=extend_schema(
        tags=["AI Inference"],
        summary="특정 추론 실행 기록 조회",
        responses=InferenceRunSerializer,
    ),
)
class InferenceRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    추론 실행 기록(InferenceRun)을 조회하는 API 뷰셋.

    - **list**: 전체 추론 실행 기록 목록
    - **retrieve**: 특정 추론 실행 기록 상세 조회
    - 권한: 관리자 전용
    """

    queryset = InferenceRun.objects.all().select_related("conversation")
    serializer_class = InferenceRunSerializer
    permission_classes = [permissions.IsAdminUser]
