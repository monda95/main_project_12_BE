from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import generics, permissions, viewsets
from django.shortcuts import get_object_or_404

from apps.core.permissions import IsOwner
from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="대화 목록 조회", tags=["Conversations"]),
    create=extend_schema(summary="새 대화 생성", tags=["Conversations"]),
    retrieve=extend_schema(summary="특정 대화 상세 조회", tags=["Conversations"]),
    update=extend_schema(summary="특정 대화 수정", tags=["Conversations"]),
    partial_update=extend_schema(summary="특정 대화 부분 수정", tags=["Conversations"]),
    destroy=extend_schema(summary="특정 대화 삭제", tags=["Conversations"]),
)
class ConversationViewSet(viewsets.ModelViewSet):
    """
    대화(Conversation) 리소스에 대한 CRUD API 뷰셋입니다.

    - **list**: 로그인 사용자가 소유한 대화 목록만 조회합니다.
    - **create**: 새로운 대화를 생성합니다. 생성 시 요청 사용자가 자동으로 소유자로 설정됩니다.
    - **retrieve**: 특정 대화의 상세 정보를 조회합니다 (소유자만 가능).
    - **partial_update**: 특정 대화의 정보를 부분적으로 수정합니다 (소유자만 가능).
    - **destroy**: 특정 대화를 삭제합니다 (소유자만 가능).
    """

    http_method_names = ["get", "post", "patch", "delete"]  # PUT 제외

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwner()]

    def get_queryset(self):
        # 로그인 사용자 소유 대화만 반환 → 다른 유저 대화 접근 차단
        return Conversation.objects.filter(owner=self.request.user).select_related(
            "owner"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        # 요청 사용자가 인증된 경우 owner로 설정, 그렇지 않으면 None으로 둠
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save(owner=None)


@extend_schema(
    summary="메시지 목록 조회 및 생성",
    tags=["Conversations"],
)
class MessageListCreateView(generics.ListCreateAPIView):
    """
    특정 대화(Conversation)에 속한 메시지를 관리하는 API 뷰
    - GET: 해당 대화의 메시지 목록 (소유자만)
    - POST: 유저 입력 메시지 추가 (role 자동 'user')
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = get_object_or_404(Conversation, id=conversation_id)
        self.check_object_permissions(self.request, conversation)
        return (
            Message.objects.filter(conversation=conversation)
            .select_related("conversation")
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        conversation_id = self.kwargs["conversation_pk"]
        conversation = get_object_or_404(Conversation, id=conversation_id)
        self.check_object_permissions(self.request, conversation)
        # role=user는 serializer에서 자동 지정
        serializer.save(conversation=conversation)
