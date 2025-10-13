import ast
import json

from django.views import View
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils.html import escape, format_html, format_html_join
from django.utils.safestring import mark_safe

from apps.inference.services import InferenceService
from apps.core.permissions import IsOwner
from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
)


ASSISTANT_GUIDE_TEXT = "🤖 Nourisher는 식품 정보에 특화된 비서예요. 음식 관련 질문을 해주세요."
ASSISTANT_FALLBACK_HTML = format_html(
    '<div class="text-gray-700">{}</div>',
    mark_safe(escape(ASSISTANT_GUIDE_TEXT).replace("\n", "<br>")),
)


def _format_user_message(text: str | None) -> str:
    if not text:
        return ""
    return mark_safe(escape(text).replace("\n", "<br>"))


def _dump_message_content(payload) -> str:
    if isinstance(payload, str):
        return payload
    if payload is None:
        return ""
    try:
        return json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(payload)


def _render_assistant_card(payload: dict) -> str:
    nutrition = payload.get("nutrition") if isinstance(payload, dict) else None
    if not isinstance(nutrition, dict):
        nutrition = {}

    macro_pairs = []
    for label, key in (
        ("열량", "calories"),
        ("단백질", "protein"),
        ("지방", "fat"),
        ("탄수화물", "carbohydrates"),
    ):
        value = nutrition.get(key)
        value_str = str(value).strip() if value not in (None, "") else ""
        if value_str:
            macro_pairs.append((label, value_str))

    macro_section = ""
    if macro_pairs:
        macro_items = format_html_join(
            "",
            "<li><span>{}</span><span>{}</span></li>",
            macro_pairs,
        )
        macro_section = format_html(
            '<ul class="assistant-card__list">{}</ul>',
            macro_items,
        )

    detail_pairs = []
    for label, key in (
        ("⚠️ 알레르기", "allergy"),
        ("📦 보관", "storage"),
        ("⚙️ 가공", "processing"),
        ("🌱 원료", "source"),
    ):
        value = payload.get(key) if isinstance(payload, dict) else None
        value_str = str(value).strip() if value not in (None, "") else ""
        if value_str:
            detail_pairs.append((label, value_str))

    detail_section = ""
    if detail_pairs:
        detail_section = format_html_join(
            "",
            '<div class="assistant-card__item"><span class="assistant-card__item-label">{}</span><span>{}</span></div>',
            detail_pairs,
        )

    if not macro_section and not detail_section:
        return ASSISTANT_FALLBACK_HTML

    header_html = format_html(
        '<header class="assistant-card__header"><h3>{}</h3><p>{}</p></header>',
        "🍽️ 영양 정보",
        "100g 기준 주요 정보를 정리했어요.",
    )

    divider_html = (
        format_html('<hr class="assistant-card__divider">')
        if macro_section and detail_section
        else ""
    )

    parts = [header_html]
    if macro_section:
        parts.append(macro_section)
    if divider_html:
        parts.append(divider_html)
    if detail_section:
        parts.append(detail_section)

    return mark_safe(
        '<article class="assistant-card" aria-label="영양 정보 카드">'
        + "".join(str(part) for part in parts)
        + "</article>"
    )


def _render_assistant_message(raw_content) -> str:
    payload = raw_content
    if isinstance(raw_content, str):
        stripped = raw_content.strip()
        if not stripped:
            payload = {}
        else:
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                try:
                    payload = ast.literal_eval(stripped)
                except (ValueError, SyntaxError):
                    payload = {"raw_text": stripped}

    if isinstance(payload, dict):
        card_html = _render_assistant_card(payload)
        if card_html != ASSISTANT_FALLBACK_HTML:
            return card_html

        raw_text = payload.get("raw_text")
        if raw_text:
            return _format_user_message(str(raw_text))

        return ASSISTANT_FALLBACK_HTML

    if isinstance(payload, str) and payload:
        return _format_user_message(payload)

    return ASSISTANT_FALLBACK_HTML


def _prepare_messages(raw_messages) -> list[dict]:
    prepared: list[dict] = []
    for msg in raw_messages:
        raw_role = getattr(msg, "role", "")
        content = getattr(msg, "content", "")

        if raw_role in (Message.Role.USER, "user"):
            prepared.append(
                {
                    "id": getattr(msg, "id", None),
                    "role": "user",
                    "display_content": _format_user_message(content),
                }
            )
        else:
            prepared.append(
                {
                    "id": getattr(msg, "id", None),
                    "role": "assistant",
                    "display_content": _render_assistant_message(content),
                }
            )

    return prepared
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

    - 로그인 사용자는 본인 소유 대화만 접근 가능
    - 익명 사용자는 세션 내에서 생성한 대화만 접근 가능
    """

    http_method_names = ["get", "post", "patch", "delete"]  # PUT 제외

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.request.user.is_authenticated:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 관리자(staff/superuser)는 전체 대화를 조회할 수 있습니다.
            if self.request.user.is_staff or self.request.user.is_superuser:
                return Conversation.objects.all().select_related("owner")

            # 로그인 사용자 → 자신의 대화만
            return Conversation.objects.filter(owner=self.request.user).select_related(
                "owner"
            )
        else:
            # 익명 사용자 → 세션 안에 기록된 대화만
            conv_ids = self.request.session.get("anonymous_conversations", [])
            return Conversation.objects.filter(id__in=conv_ids)

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            conversation = serializer.save(owner=None)
            conv_ids = self.request.session.get("anonymous_conversations", [])
            conv_ids.append(conversation.id)
            self.request.session["anonymous_conversations"] = conv_ids


@extend_schema(
    summary="메시지 목록 조회 및 생성",
    tags=["Conversations"],
)
class MessageListCreateView(generics.ListCreateAPIView):
    """
    특정 대화(Conversation)에 속한 메시지를 관리하는 API 뷰
    - GET: 해당 대화의 메시지 목록
    - POST: 유저 입력 메시지 추가 후, AI 응답을 함께 반환
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]  # 익명도 허용

    def get_conversation(self):
        conversation = get_object_or_404(
            Conversation, id=self.kwargs["conversation_pk"]
        )

        if self.request.user.is_authenticated:
            if not (
                self.request.user.is_staff
                or self.request.user.is_superuser
                or conversation.owner_id == self.request.user.id
            ):
                raise PermissionDenied("이 대화에 접근할 권한이 없습니다.")
        else:
            conv_ids = self.request.session.get("anonymous_conversations", [])
            if conversation.id not in conv_ids:
                raise PermissionDenied("이 대화에 접근할 권한이 없습니다.")
        return conversation

    def get_queryset(self):
        conversation = self.get_conversation()
        return (
            Message.objects.filter(conversation=conversation)
            .select_related("conversation")
            .order_by("created_at")
        )

    def create(self, request, *args, **kwargs):
        """POST 시 user+ai 메시지를 DB 저장 후, 묶어서 반환"""
        conversation = self.get_conversation()
        user_content = request.data.get("content", "").strip()

        if not user_content:
            return JsonResponse(
                {"detail": "내용이 비어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. 유저 메시지 저장
        user_msg = Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=user_content,
        )

        # 2. AI 응답 생성 및 저장
        result = InferenceService.run_inference(
            conversation_id=conversation.id,
            prompt=user_content,
            user=request.user if request.user.is_authenticated else None,
            options={},
        )
        ai_raw_content = result.get("content", "")
        ai_msg = Message.objects.create(
            conversation=conversation,
            role=Message.Role.AI,
            content=_dump_message_content(ai_raw_content),
        )

        # 3. 두 메시지를 묶어서 응답
        return JsonResponse(
            {
                "messages": [
                    {"id": user_msg.id, "role": "user", "content": user_msg.content},
                    {"id": ai_msg.id, "role": "assistant", "content": ai_msg.content},
                ]
            },
            status=status.HTTP_201_CREATED,
        )


class ConversationPageView(View):
    template_name = "conversation.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", "").strip()
        conversation_id_param = request.GET.get("conversation_id")
        conversation = None
        messages = []

        if conversation_id_param:
            try:
                conversation_id_int = int(conversation_id_param)
            except (TypeError, ValueError):
                conversation_id_int = None

            if conversation_id_int is not None:
                conversation = get_object_or_404(Conversation, id=conversation_id_int)

                if request.user.is_authenticated:
                    if not (
                        request.user.is_staff
                        or request.user.is_superuser
                        or conversation.owner_id == request.user.id
                    ):
                        return render(
                            request,
                            self.template_name,
                            {
                                "conversation": None,
                                "conversation_id": None,
                                "messages": [],
                            },
                            status=status.HTTP_200_OK,
                        )
                else:
                    conv_ids = request.session.get("anonymous_conversations", [])
                    if conversation.id not in conv_ids:
                        return render(
                            request,
                            self.template_name,
                            {
                                "conversation": None,
                                "conversation_id": None,
                                "messages": [],
                            },
                            status=status.HTTP_200_OK,
                        )

                messages = list(
                    Message.objects.filter(conversation=conversation)
                    .order_by("created_at")
                )

        elif query:
            # 1. 대화 생성
            if request.user.is_authenticated:
                conversation = Conversation.objects.create(
                    owner=request.user, title=query
                )
            else:
                conversation = Conversation.objects.create(owner=None, title=query)
                conv_ids = request.session.get("anonymous_conversations", [])
                conv_ids.append(conversation.id)
                request.session["anonymous_conversations"] = conv_ids

            # 2. 유저 메시지 저장
            user_msg = Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=query,
            )

            # 3. AI 응답 저장
            result = InferenceService.run_inference(
                conversation_id=conversation.id,
                prompt=query,
                user=request.user if request.user.is_authenticated else None,
                options={},
            )
            ai_raw_content = result.get("content", "")
            ai_msg = Message.objects.create(
                conversation=conversation,
                role=Message.Role.AI,
                content=_dump_message_content(ai_raw_content),
            )

            messages = [user_msg, ai_msg]

        prepared_messages = _prepare_messages(messages)

        return render(
            request,
            self.template_name,
            {
                "conversation": conversation,
                "conversation_id": conversation.id if conversation else None,
                "messages": prepared_messages,
            },
        )
