from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    PasswordChangeSerializer,
    RefreshTokenSerializer,
    SignupSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


@extend_schema(tags=["인증/권한"])
class SignupView(generics.CreateAPIView):
    """
    회원가입 API

    - 인증 불필요, 누구나 접근가능
    - 새로운 사용자 생성
    """

    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["사용자"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    내 정보 관리 API (/users/me/)

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
    비밀번호 변경 API

    - current_password 오류 → 400 반환
    - new_password 불일치 → 400 반환
    - 성공 시 비밀번호 갱신
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["인증/권한"])
class LogoutView(generics.GenericAPIView):
    """
    로그아웃 API

    - 클라이언트에서 받은 refresh 토큰을 블랙리스트 처리
    """

    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = RefreshToken(serializer.validated_data["refresh"])
            refresh_token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["인증/권한"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    로그인 API (JWT access/refresh 발급)
    """

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["인증/권한"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    토큰 갱신 API (refresh → access 재발급)
    """

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
