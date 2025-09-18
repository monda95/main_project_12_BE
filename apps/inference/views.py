from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from apps.conversations.models import Conversation, Message
from .models import InferenceRun
from .serializers import (
    InferenceRequestSerializer,
    InferenceResponseSerializer,
    InferenceRunSerializer,
)
from .services import call_gemini_api  # services에서 임포트

MODEL_NAME = "gemini-2.5-flash"  # 모델명 상수화


@extend_schema(
    summary="[생성] Gemini 추론 호출",
    request=InferenceRequestSerializer,
    responses=InferenceResponseSerializer,
    tags=["AI 추론"],
    operation_id="Inference__create",
)
class InferenceView(APIView):
    """
    Gemini API를 호출하여 AI 추론을 실행하고, 관련된 데이터를 저장합니다.

    - **POST**: 사용자의 프롬프트를 받아 Gemini API로 전달합니다.
    - API 호출이 성공하면, 사용자 메시지(user)와 AI의 응답(assistant)을 `Message` 객체로 저장합니다.
    - 또한, API 호출에 대한 상세 정보(지연 시간, 토큰 사용량 등)를 `InferenceRun` 객체로 기록합니다.

    **권한**: 인증된 사용자만 접근 가능합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs) -> Response:
        # 요청 데이터 유효성 검증
        req_ser = InferenceRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 유효한 데이터 추출
        conversation_id = req_ser.validated_data["conversation_id"]
        prompt_content: str = req_ser.validated_data["prompt"]
        options: dict = req_ser.validated_data.get("options", {}) or {}

        # 1) 소유자 기준으로 대화 조회
        conversation = get_object_or_404(
            Conversation.objects.select_for_update(),  # 동시성 안전
            id=conversation_id,
            owner=request.user,
        )

        # 2) 사용자 메시지 저장
        user_msg = Message.objects.create(
            conversation=conversation,
            role="user",
            content=prompt_content,
        )

        # 3) Gemini 호출
        gemini = call_gemini_api(prompt_content, options)
        ai_content = gemini.get("ai_content") or "API 응답을 받지 못했습니다."
        latency_ms = gemini.get("latency_ms") or 0
        prompt_tokens = gemini.get("prompt_tokens")
        completion_tokens = gemini.get("completion_tokens")
        status_str = gemini.get("status")
        error_code = gemini.get("error_code")
        error_message = gemini.get("error_message")  # 신규 필드 추가 내용

        # 4) AI 응답 메시지 저장
        ai_msg = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_content,
        )

        # 5) 추론 실행 로그 저장 (error_message 포함)
        InferenceRun.objects.create(
            conversation=conversation,
            message=ai_msg,
            model=MODEL_NAME,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status=status_str,
            error_code=error_code,
            error_message=error_message,
        )

        # 6) 응답용 usage 정규화(권장안) — 실패 시만 0으로 변환 → 클라이언트는 항상 정수라고 가정 가능

        resp_prompt_tokens = (
            (prompt_tokens or 0) if status_str == "error" else prompt_tokens
        )
        resp_completion_tokens = (
            (completion_tokens or 0) if status_str == "error" else completion_tokens
        )

        # 7) 응답 직렬화
        resp = {
            "message_id": ai_msg.id,
            "role": ai_msg.role,
            "content": ai_msg.content,
            "usage": {
                "prompt_tokens": resp_prompt_tokens,
                "completion_tokens": resp_completion_tokens,
            },
        }
        out_ser = InferenceResponseSerializer(resp)
        return Response(out_ser.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="[목록] 추론 실행 기록 조회",
        tags=["추론 모니터링"],
        operation_id="InferenceRun__list",
    ),
    retrieve=extend_schema(
        summary="[조회] 특정 추론 실행 기록 조회",
        tags=["추론 모니터링"],
        operation_id="InferenceRun__retrieve",
    ),
)
class InferenceRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    추론 실행 기록(InferenceRun)을 조회하는 API 뷰셋입니다.

    - **list**: 모든 추론 실행 기록 목록을 조회합니다.
    - **retrieve**: 특정 추론 실행 기록의 상세 정보를 조회합니다.

    **권한**: 관리자만 접근 가능합니다.
    """

    queryset = InferenceRun.objects.all().select_related("conversation", "message")
    serializer_class = InferenceRunSerializer
    permission_classes = [permissions.IsAdminUser]
