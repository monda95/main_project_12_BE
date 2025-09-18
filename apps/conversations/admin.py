from django.contrib import admin

from .models import Conversation, Message


# 1. Message를 Conversation과 함께 편집하기 위한 Inline 클래스 정의
class MessageInline(admin.TabularInline):
    model = Message
    # 인라인 폼에서 보여줄 필드
    fields = ("role", "content", "created_at")
    # created_at은 자동 생성되므로 읽기 전용으로 설정
    readonly_fields = ("created_at",)
    # 추가로 입력할 수 있는 빈 메시지 폼 개수
    extra = 1


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", "owner")
    search_fields = ("title", "owner__email")
    raw_id_fields = ("owner",)
    # 2. Conversation 관리자 페이지에 Message 인라인 등록
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # 3. (개선) 전체 내용 대신 일부만 보이도록 함수 사용
    list_display = ("id", "conversation", "role", "content_snippet", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "conversation__title")
    raw_id_fields = ("conversation",)

    def content_snippet(self, obj):
        """내용이 50자 이상이면 ...으로 축약해서 보여줍니다."""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content

    # 관리자 페이지에 표시될 컬럼의 제목을 설정
    content_snippet.short_description = "내용 (일부)"
