from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet, MessageListCreateView, TagViewSet

app_name = "conversations"

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
    # 중첩된 메시지 URL: /api/v1/conversations/{conversation_pk}/messages/
    path(
        "conversations/<int:conversation_pk>/messages/",
        MessageListCreateView.as_view(),
        name="message-list-create",
    ),
]
