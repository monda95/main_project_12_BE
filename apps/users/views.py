from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes

# from django.core.mail import send_mail
# from django.conf import settings
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

    def perform_create(self, serializer):
        user = serializer.save()
        transaction.on_commit(lambda: self.send_verification_email(user))

    def send_verification_email(self, user):
        """
        이메일 인증을 위한 이메일 발송 로직
        터미널에서 링크 클릭으로 처리되므로, 이메일 인증 완료를 가정한 로직
        """
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # 인증 링크 생성
        verification_link = self.request.build_absolute_uri(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )

        # 실제 이메일 발송 (주석처리 후 테스트로 인증처리 가능)
        # send_mail(
        #     "이메일 인증",
        #     f"이메일 인증을 위해 아래 링크를 클릭하세요:\n{verification_link}",
        #     settings.DEFAULT_FROM_EMAIL,
        #     [user.email],
        #     fail_silently=False,
        # )

        print(f"인증 링크: {verification_link} (터미널에서 클릭 시 인증 처리됨)")

        # docker compose logs web 로 로컬에서 docker compose만으로 서버 띄우고 있더라도 확인가능.


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
        email = (request.data.get("email") or "").strip()
        # 대소문자 무시하고 사용자 조회
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.email_verified_at:
            return Response({"detail": "이메일 인증이 필요합니다."}, status=400)
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["인증/권한"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    토큰 갱신 API (refresh → access 재발급)
    """

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return HttpResponse("잘못된 인증 링크입니다.", status=400)

    if default_token_generator.check_token(user, token):
        user.email_verified_at = timezone.now()
        user.save()
        return HttpResponse("이메일 인증이 완료되었습니다.", status=200)
    else:
        return HttpResponse("잘못된 인증 링크입니다.", status=400)
