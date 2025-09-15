from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,  # extend_schema_view 대신 extend_schema 임포트
)
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.conversations.models import Conversation, Message

from .models import InferenceRun
from .serializers import (
    InferenceRequestSerializer,
    InferenceResponseSerializer,
    InferenceRunSerializer,
)
from .services import call_gemini_api  # services.py에서 함수 임포트


class InferenceView(APIView):
    """
    Gemini API 호출을 통해 AI 응답을 생성하고 저장하는 API 뷰입니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=InferenceRequestSerializer,  # 요청 시리얼라이저 명시
        responses=InferenceResponseSerializer,  # 응답 시리얼라이저 명시
        tags=["AI 추론"],  # 태그 명시
    )
    def post(self, request, *args, **kwargs):
        serializer = InferenceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data["conversation_id"]
        prompt_content = serializer.validated_data["prompt"]
        options = serializer.validated_data.get("options", {})

        # 1. 대화 객체 가져오기 및 소유자 권한 확인
        conversation = get_object_or_404(Conversation, id=conversation_id)
        # IsOwner 권한은 객체 레벨에서 작동하므로, 수동으로 확인
        if conversation.owner != request.user:
            return Response(
                {"detail": "이 대화에 접근할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2. 사용자 메시지 저장 (선택사항이지만 대화 흐름상 필요)
        user_message = Message.objects.create(
            conversation=conversation, role="user", content=prompt_content
        )

        # 3. Gemini API 호출 및 결과 처리
        gemini_response = call_gemini_api(prompt_content, options)

        ai_response_content = gemini_response["ai_content"]
        latency_ms = gemini_response["latency_ms"]
        prompt_tokens = gemini_response["prompt_tokens"]
        completion_tokens = gemini_response["completion_tokens"]
        status_str = gemini_response["status"]
        error_code = gemini_response["error_code"]

        # 4. AI 응답 메시지 저장
        ai_message = Message.objects.create(
            conversation=conversation, role="assistant", content=ai_response_content
        )

        # 5. 추론 기록 저장
        inference_run = InferenceRun.objects.create(
            conversation=conversation,
            message=ai_message,  # AI 응답 메시지와 연결
            model="gemini-flash",  # 사용 모델명 (실제 호출 모델명으로 대체 가능)
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status=status_str,
            error_code=error_code,
        )

        # 6. 응답 시리얼라이즈
        response_data = {
            "message_id": ai_message.id,
            "role": ai_message.role,
            "content": ai_message.content,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        }
        serializer = InferenceResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InferenceRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    추론 실행 기록(InferenceRun)을 조회하는 API 뷰셋입니다。
    관리자만 접근 가능합니다.
    """

    queryset = InferenceRun.objects.all().select_related("conversation", "message")
    serializer_class = InferenceRunSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=["추론 모니터링"])  # 각 메서드에 추가
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["추론 모니터링"])  # 각 메서드에 추가
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
