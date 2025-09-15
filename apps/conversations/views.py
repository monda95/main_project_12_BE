from drf_spectacular.utils import (
    extend_schema,  # extend_schema_view 대신 extend_schema 임포트
)
from rest_framework import generics, permissions, viewsets

from apps.core.permissions import IsOwner

from .models import Conversation, Message, Tag
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
    TagSerializer,
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    대화(Conversation) 리소스에 대한 CRUD API 뷰셋입니다.
    목록 조회, 생성, 상세 조회, 수정, 삭제를 지원합니다.
    """

    queryset = (
        Conversation.objects.all().select_related("owner").prefetch_related("tags")
    )
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        # 생성 시 요청을 보낸 사용자를 owner로 자동 설정
        serializer.save(owner=self.request.user)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["대화/메시지"])  # 각 메서드에 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    """
    태그(Tag) 리소스에 대한 CRUD API 뷰셋입니다.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 태그 이름 중복 검사는 모델의 save() 메서드에서 처리 (소문자 변환)
        serializer.save()

    def get_object(self):
        # 태그는 소유자가 없으므로, 모든 사용자가 접근 가능하도록 기본 get_object 사용
        # 단, 권한은 IsAuthenticated로 제한
        return super().get_object()

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(tags=["태그"])  # 각 메서드에 추가
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
