from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    객체의 소유자(owner)가 요청을 보낸 사용자(request.user)와 동일한 경우에만
    쓰기/수정/삭제 권한을 허용하는 커스텀 권한입니다.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS(GET, HEAD, OPTIONS)에 대해서는 모든 요청을 허용합니다.
        # (예: 다른 사람도 게시물 내용을 읽을 수는 있어야 하므로)
        # 만약 읽기조차 소유자만 가능하게 하려면 이 부분을 수정해야 합니다.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 관리자(staff/superuser)면 무조건 허용
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        # 소유자(owner)만 허용
        # 쓰기, 수정, 삭제 권한은 객체의 `owner` 속성이
        # 요청을 보낸 사용자와 일치하는 경우에만 부여됩니다.
        # 이 코드가 동작하려면 해당 객체(obj)에 `owner`라는 속성이 있어야 합니다.
        return obj.owner == request.user
