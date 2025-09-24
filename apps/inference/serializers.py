from rest_framework import serializers

from .models import InferenceRun


class InferenceRequestSerializer(serializers.Serializer):
    """
    Gemini 호출을 위한 요청 시리얼라이저입니다.
    """

    conversation_id = serializers.IntegerField(
        required=False, help_text="대화 ID (없으면 새 대화 생성)"
    )
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


class SelfCheckSerializer(serializers.Serializer):
    """
    Self-Check 결과 정보를 위한 중첩 시리얼라이저입니다.
    """

    check_pass = serializers.BooleanField()
    retry_used = serializers.BooleanField()
    violations = serializers.ListField(child=serializers.JSONField(), allow_empty=True)


class InferenceResponseSerializer(serializers.Serializer):
    """
    Gemini 호출 후 응답을 위한 시리얼라이저입니다.
    """

    message_id = serializers.IntegerField(help_text="생성된 메시지 ID")
    role = serializers.CharField(help_text="메시지 역할 (assistant)")
    content = serializers.JSONField(help_text="AI 응답 내용 (구조화된 JSON)")
    usage = UsageSerializer(help_text="API 사용량 정보")
    self_check = SelfCheckSerializer(help_text="Self-Check 결과")


class InferenceRunSerializer(serializers.ModelSerializer):
    """
    추론 실행 기록 조회를 위한 시리얼라이저입니다.
    """

    owner_email = serializers.CharField(
        source="conversation.owner.email", read_only=True, allow_null=True
    )
    conversation_title = serializers.CharField(
        source="conversation.title", read_only=True
    )

    class Meta:
        model = InferenceRun
        fields = [
            "id",
            "owner_email",
            "conversation_title",
            "model",
            "latency_ms",
            "prompt_tokens",
            "completion_tokens",
            "status",
            "error_code",
            "check_pass",
            "retry_used",
            "violations",
            "created_at",
        ]
