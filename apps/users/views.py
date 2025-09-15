from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    extend_schema,  # extend_schema_view 대신 extend_schema 임포트
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (  # 이 줄 추가
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    PasswordChangeSerializer,
    RefreshTokenSerializer,
    SignupSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class SignupView(generics.CreateAPIView):
    """
    회원가입을 처리하는 API 뷰입니다。
    누구나 접근할 수 있도록 `permission_classes`를 `AllowAny`로 설정합니다。
    """

    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]  # 회원가입은 인증 없이 허용

    @extend_schema(tags=["인증/권한"])  # 이 데코레이터 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["사용자"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    /users/me/
    - GET: 내 정보 조회
    - PUT/PATCH: 내 정보 수정
    - DELETE: 탈퇴 (soft delete)
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserDetailSerializer

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {"detail": "계정이 비활성화되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )


@extend_schema(tags=["사용자"])
class PasswordChangeView(generics.UpdateAPIView):
    """
    현재 로그인한 사용자의 비밀번호를 변경합니다.

    - current_password가 올바르지 않으면 400 에러 반환
    - new_password와 new_password_confirm 불일치 시 400 에러 반환
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        if not user.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"current_password": "현재 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data["new_password"]
        confirm_password = serializer.validated_data.get("new_password_confirm")

        if new_password != confirm_password:
            return Response(
                {"new_password_confirm": "새 비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK
        )


class LogoutView(generics.GenericAPIView):
    """
    로그아웃을 처리합니다. 클라이언트로부터 받은 refresh 토큰을 블랙리스트에 추가합니다.
    """

    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["인증/권한"])  # 이 데코레이터 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# simple_jwt 뷰를 위한 프록시 뷰
class CustomTokenObtainPairView(TokenObtainPairView):
    @extend_schema(tags=["인증/권한"])  # 이 데코레이터 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["인증/권한"])  # 이 데코레이터 추가
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
