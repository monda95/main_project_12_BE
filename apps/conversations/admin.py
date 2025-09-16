from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "owner")
    search_fields = ("title", "owner__email")
    raw_id_fields = ("owner",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "content", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "conversation__title")
    raw_id_fields = ("conversation",)
