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
from .models import OAuthAccount
from .utils import complete_oauth_flow, issue_jwt_for_user, OAuthError

# from django.core.mail import send_mail
# from django.conf import settings
from .serializers import (
    PasswordChangeSerializer,
    RefreshTokenSerializer,
    SignupSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    OAuthExchangeSerializer,
    OAuthLinkSerializer,
)

User = get_user_model()


@extend_schema(summary="[생성] 회원가입", tags=["인증/권한"])
class SignupView(generics.CreateAPIView):
    """
    회원가입 API

    - 인증이 불필요하며, 누구나 접근할 수 있습니다.
    - 새로운 사용자를 생성하고 인증 이메일을 발송합니다.
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


@extend_schema(summary="[조회/수정/탈퇴] 내 정보 관리", tags=["사용자"])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    내 정보 관리 API (/users/me/)

    - **GET**: 내 정보 조회를 처리합니다.
    - **PATCH**: 내 정보 수정을 처리합니다. (부분 수정만으로도 수정허용)
    - **DELETE**: 회원 탈퇴를 처리합니다. (Soft Delete)
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]  # PUT 제외

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserDetailSerializer

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.deactivated_at = timezone.now()  # ⬅탈퇴시점 기록(부분 인덱스와 정합)
        user.save(update_fields=["is_active", "deactivated_at", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="[수정] 비밀번호 변경", tags=["사용자"])
class PasswordChangeView(generics.UpdateAPIView):
    """
    비밀번호 변경 API

    - `current_password`가 틀릴 경우 400 에러를 반환합니다.
    - `new_password`와 `new_password_confirm`이 일치하지 않을 경우 400 에러를 반환합니다.
    - 성공 시 사용자의 비밀번호를 새로 갱신합니다.
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


@extend_schema(summary="[인증] 로그아웃", tags=["인증/권한"])
class LogoutView(generics.GenericAPIView):
    """
    로그아웃 API

    - 클라이언트로부터 받은 **Refresh Token을 블랙리스트에 추가**하여 더 이상 사용할 수 없도록 처리합니다.
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


@extend_schema(summary="[인증] 로그인 (토큰 발급)", tags=["인증/권한"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    로그인 API

    - 사용자 이메일과 비밀번호를 확인하여 유효한 경우, **JWT Access Token과 Refresh Token을 발급**합니다.
    - 이메일 인증이 완료되지 않은 사용자는 로그인이 제한됩니다.
    """

    def post(self, request, *args, **kwargs):
        # 1) 입력 이메일 정규화
        email = (request.data.get("email") or "").strip().lower()

        # 2) 운영 플래그에 따른 이메일 인증 강제
        user = User.objects.filter(email=email).first()
        # settings를 직접 참조하거나 from django.conf import settings 후 settings.AUTH_EMAIL_VERIFICATION_REQUIRED 사용
        from django.conf import settings

        if user and getattr(settings, "AUTH_EMAIL_VERIFICATION_REQUIRED", False):
            if not user.email_verified_at:
                return Response(
                    {"detail": "이메일 인증이 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # ⬇실제 인증에 쓰일 payload도 정규화된 email로 교체
        data = request.data.copy()
        data["email"] = email
        request._full_data = data  # DRF Request 캐시 갱신

        # ⬇토큰 발급 로직 실행
        return super().post(request, *args, **kwargs)


@extend_schema(summary="[인증] 토큰 갱신", tags=["인증/권한"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    토큰 갱신 API

    - 만료된 **Access Token**을 유효한 **Refresh Token**을 사용하여 새로 재발급받습니다.
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


@extend_schema(tags=["인증"], summary="[OAuth2] 코드 교환 → 로그인/가입", exclude=True)
class OAuthExchangeView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OAuthExchangeSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            user, is_new, _ = complete_oauth_flow(login_user=None, **s.validated_data)
        except OAuthError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = issue_jwt_for_user(user)
        body = {
            **tokens,
            "is_new": is_new,
            "user": {"id": user.id, "email": user.email},
        }
        return Response(body, status=status.HTTP_200_OK)


@extend_schema(
    tags=["인증"],
    summary="[OAuth2] 소셜 계정 연결",
    responses={204: None},
    exclude=True,
)
class OAuthLinkView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OAuthLinkSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        # 이미 동일 provider 연결이 있으면 409
        if OAuthAccount.objects.filter(
            user=request.user, provider=s.validated_data["provider"]
        ).exists():
            return Response(
                {"detail": "이미 연결된 공급자입니다."}, status=status.HTTP_409_CONFLICT
            )
        try:
            _, _, _ = complete_oauth_flow(login_user=request.user, **s.validated_data)
        except OAuthError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["인증"],
    summary="[OAuth2] 소셜 계정 연결 해제",
    responses={204: None},
    exclude=True,
)
class OAuthUnlinkView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "provider"  # URL 경로 파라미터로 공급자 지정

    def delete(self, request, provider: str, *args, **kwargs):
        qs = OAuthAccount.objects.filter(user=request.user, provider=provider)
        if not qs.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        # 보호: 마지막 로그인 수단이면 차단(패스워드 미설정 + 소셜 1개)
        if (
            not request.user.has_usable_password()
            and request.user.oauth_accounts.count() <= 1
        ):
            return Response(
                {"detail": "마지막 로그인 수단은 해제할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # .env에 각 provider client/secret/redirect 설정
    # 개발 단계: exchange_code_for_claims에 더미 구현으로 테스트 → 운영 전 실제 HTTP 교환/검증 로직으로 교체
    # swagger에 등록 안 할 계획
    # (선택) 뷰에 `@extend_schema(exclude=True)` 적용 또는
    # (선택) `SPECTACULAR_SETTINGS["EXCLUDE_PATHS"] = [r"^/api/v1/auth/verify/"]`
