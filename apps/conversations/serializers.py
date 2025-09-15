from rest_framework import serializers

from .models import Conversation, Message, Tag


class ConversationSerializer(serializers.ModelSerializer):
    """
    대화 목록 조회 및 상세 조회를 위한 시리얼라이저입니다.
    """

    owner = serializers.ReadOnlyField(source="owner.email")  # 소유자 이메일 표시
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )  # 태그 이름 목록 표시

    class Meta:
        model = Conversation
        fields = ["id", "title", "owner", "tags", "created_at", "updated_at"]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    새 대화를 생성하기 위한 시리얼라이저입니다.
    """

    class Meta:
        model = Conversation
        fields = ["title"]

    def create(self, validated_data):
        # 뷰에서 context로 request.user를 넘겨받아 owner를 설정합니다.
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    """
    메시지 목록 조회 및 생성을 위한 시리얼라이저입니다.
    """

    # conversation 필드는 URL에서 결정되므로, 읽기 전용으로 설정합니다.
    conversation = serializers.ReadOnlyField(source="conversation.id")

    class Meta:
        model = Message
        fields = ["id", "conversation", "role", "content", "created_at"]
        read_only_fields = [
            "conversation"
        ]  # 생성 시 conversation은 request.data가 아닌 URL에서 가져옴


class TagSerializer(serializers.ModelSerializer):
    """
    태그 목록 조회 및 생성을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = Tag
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]  # 생성 시 created_at은 자동 생성
