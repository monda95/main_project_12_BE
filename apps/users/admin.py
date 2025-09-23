from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, OAuthAccount


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Django 관리자 페이지에서 User 모델을 관리하기 위한 클래스입니다.
    """

    # UserAdmin의 기본 필드 구성을 그대로 사용하면서, 커스텀 필드를 추가합니다.
    # User 모델의 fieldsets를 확장합니다.
    fieldsets = UserAdmin.fieldsets + (("추가 정보", {"fields": ("nickname",)}),)

    # 관리자 페이지 목록에 보일 필드를 지정합니다.
    list_display = (
        "id",
        "email",
        "username",
        "nickname",
        "is_staff",
        "is_active",
        "created_at",
    )

    # 목록에서 필터링할 수 있는 필드를 지정합니다.
    list_filter = UserAdmin.list_filter + ("created_at",)

    # 검색 필드를 지정합니다.
    search_fields = ("email", "username", "nickname")

    # 정렬 순서를 지정합니다.
    ordering = ("-created_at",)


@admin.register(OAuthAccount)
class OAuthAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "provider",
        "subject",
        "email",
        "email_verified",
        "created_at",
    )
    list_filter = ("provider", "email_verified", "created_at")
    search_fields = ("user__email", "subject", "email")
    autocomplete_fields = ("user",)
