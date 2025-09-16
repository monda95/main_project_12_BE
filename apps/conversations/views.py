from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import generics, permissions, viewsets

from apps.core.permissions import IsOwner

from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["대화/메시지"]),
    create=extend_schema(tags=["대화/메시지"]),
    retrieve=extend_schema(tags=["대화/메시지"]),
    update=extend_schema(tags=["대화/메시지"]),
    partial_update=extend_schema(tags=["대화/메시지"]),
    destroy=extend_schema(tags=["대화/메시지"]),
)
class ConversationViewSet(viewsets.ModelViewSet):
    """
    대화(Conversation) 리소스에 대한 CRUD API 뷰셋입니다.
    목록 조회, 생성, 상세 조회, 수정, 삭제를 지원합니다.
    """

    queryset = Conversation.objects.all().select_related("owner")
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        # 생성 시 요청을 보낸 사용자를 owner로 자동 설정
        serializer.save(owner=self.request.user)


@extend_schema(tags=["대화/메시지"])
class MessageListCreateView(generics.ListCreateAPIView):
    """
    특정 대화(Conversation)에 속한 메시지 목록을 조회하거나 새 메시지를 추가합니다.
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # URL에서 conversation_id를 가져와 해당 대화의 메시지만 필터링
        conversation_id = self.kwargs["conversation_pk"]
        return (
            Message.objects.filter(conversation__id=conversation_id)
            .select_related("conversation")
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        # 메시지 생성 시 해당 대화에 연결
        conversation_id = self.kwargs["conversation_pk"]
        conversation = Conversation.objects.get(id=conversation_id)
        # 권한 검사: 메시지를 생성하려는 대화의 소유자가 현재 사용자인지 확인
        self.check_object_permissions(self.request, conversation)  # IsOwner 권한 검사
        serializer.save(conversation=conversation)
