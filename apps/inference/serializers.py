from rest_framework import serializers

from .models import InferenceRun


class InferenceRequestSerializer(serializers.Serializer):
    """
    Gemini 호출을 위한 요청 시리얼라이저입니다.
    """

    conversation_id = serializers.IntegerField(help_text="대화 ID")
    prompt = serializers.CharField(help_text="사용자 프롬프트 내용")
    options = serializers.JSONField(
        required=False,
        help_text="Gemini API 호출 옵션 (temperature, max_output_tokens 등)",
    )


class UsageSerializer(serializers.Serializer):
    """
    API 사용량(토큰) 정보를 위한 중첩 시리얼라이저입니다.
    """

    prompt_tokens = serializers.IntegerField()
    completion_tokens = serializers.IntegerField()


class InferenceResponseSerializer(serializers.Serializer):
    """
    Gemini 호출 후 응답을 위한 시리얼라이저입니다.
    """

    message_id = serializers.IntegerField(help_text="생성된 메시지 ID")
    role = serializers.CharField(help_text="메시지 역할 (assistant)")
    content = serializers.CharField(help_text="AI 응답 내용")
    usage = UsageSerializer(help_text="API 사용량 정보")


class InferenceRunSerializer(serializers.ModelSerializer):
    """
    추론 실행 기록 조회를 위한 시리얼라이저입니다.
    """

    conversation = serializers.ReadOnlyField(
        source="conversation.title"
    )  # 대화 제목 표시
    message = serializers.ReadOnlyField(source="message.content")  # 메시지 내용 표시

    class Meta:
        model = InferenceRun
        fields = [
            "id",
            "conversation",
            "message",
            "model",
            "latency_ms",
            "prompt_tokens",
            "completion_tokens",
            "status",
            "error_code",
            "error_message",
            "created_at",
        ]
