from rest_framework import serializers

from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    """
    대화 목록 조회 및 상세 조회를 위한 시리얼라이저입니다.
    """

    owner = serializers.ReadOnlyField(source="owner.email")  # 소유자 이메일 표시

    class Meta:
        model = Conversation
        fields = ["id", "title", "owner", "created_at", "updated_at"]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    새 대화를 생성하기 위한 시리얼라이저입니다.
    """

    class Meta:
        model = Conversation
        fields = ["title"]


class MessageSerializer(serializers.ModelSerializer):
    """
    메시지 목록 조회 및 생성을 위한 시리얼라이저
    - 클라이언트는 content만 입력
    - role은 자동으로 'user'로 강제됨
    """

    conversation = serializers.ReadOnlyField(source="conversation.id")

    class Meta:
        model = Message
        fields = ["id", "conversation", "role", "content", "created_at"]
        read_only_fields = ["conversation", "role"]

    def create(self, validated_data):
        # role을 강제로 user로 지정
        validated_data["role"] = Message.Role.USER
        return super().create(validated_data)
