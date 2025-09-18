from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Conversation/Message 소유자만 접근할 수 있는 권한.
    - SAFE_METHODS(GET 포함)도 소유자만 허용.
    - 관리자(staff/superuser)는 항상 허용.
    """

    def has_object_permission(self, request, view, obj):
        # 관리자(staff/superuser)는 무조건 허용
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        # Conversation 객체라면
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # Message 객체라면
        if hasattr(obj, "conversation"):
            return obj.conversation.owner == request.user

        return False
