import logging
import requests
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth import logout as django_logout  # PATCH: 세션 로그아웃
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, FormView
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.http import JsonResponse
from django.conf import settings
from urllib.parse import urlencode

# PATCH: CSRF/Decorator/APIView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from .forms import SignupForm, LoginForm
from .serializers import (
    PasswordChangeSerializer,
    RefreshTokenSerializer,
    SignupSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


def _build_github_redirect_uri(request):
    github_settings = settings.OAUTH_CLIENTS.get("github", {})
    redirect_uri = github_settings.get("redirect_uri")
    if redirect_uri:
        return redirect_uri
    return request.build_absolute_uri(reverse("github_callback"))


def send_verification_email(request, user):
    """이메일 인증을 위한 이메일 발송 로직"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verification_link = request.build_absolute_uri(
        reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    )

    print(f"인증 링크: {verification_link} (터미널에서 클릭 시 인증 처리됨)")


@extend_schema(summary="[생성] 회원가입", tags=["Auth & Users"])
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
        transaction.on_commit(lambda: send_verification_email(self.request, user))


class LoginPageView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("main-page")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)
        if user is None:
            form.add_error(None, "이메일 또는 비밀번호가 올바르지 않습니다.")
            return self.form_invalid(form)
        login(self.request, user)

        # 비회원 시절에 생성된 대화 목록은 로그인 후 노출되지 않도록 정리합니다.
        if "anonymous_conversations" in self.request.session:
            del self.request.session["anonymous_conversations"]

        return super().form_valid(form)


class SignupPageView(TemplateView):
    template_name = "signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", kwargs.get("form", SignupForm()))
        return context

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            serializer = SignupSerializer(data=form.build_serializer_payload())
            if serializer.is_valid():
                user = serializer.save()
                transaction.on_commit(lambda: send_verification_email(request, user))
                return redirect("login-page")
            self._bind_serializer_errors_to_form(serializer, form)
        return self.render_to_response(self.get_context_data(form=form))

    @staticmethod
    def _bind_serializer_errors_to_form(serializer, form):
        error_dict = serializer.errors
        for field, errors in error_dict.items():
            if not isinstance(errors, (list, tuple)):
                errors = [errors]

            if field == "non_field_errors":
                target_field = None
            elif field in form.fields:
                target_field = field
            else:
                target_field = None

            for error in errors:
                form.add_error(target_field, error)


@extend_schema(summary="[조회/수정/탈퇴] 내 정보 관리", tags=["Auth & Users"])
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


@extend_schema(summary="[수정] 비밀번호 변경", tags=["Auth & Users"])
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


@extend_schema(summary="[인증] 로그아웃", tags=["Auth & Users"])
class LogoutView(generics.GenericAPIView):
    """
    로그아웃 API

    - 클라이언트로부터 받은 **Refresh Token을 블랙리스트에 추가**하여 더 이상 사용할 수 없도록 처리합니다.
    """

    serializer_class = RefreshTokenSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes: list = []

    def post(self, request, *args, **kwargs):
        refresh_value = request.data.get("refresh")
        user = request.user if request.user.is_authenticated else None

        if not refresh_value:
            if user and user.is_superuser:
                logger.info(
                    "[로그아웃] 슈퍼유저 %s가 토큰 없이 로그아웃을 완료했습니다.",
                    getattr(user, "email", user.get_username()),
                )
            elif user:
                logger.info(
                    "[로그아웃] 사용자 %s가 토큰 없이 로그아웃을 요청하여 추가 조치 없이 종료했습니다.",
                    getattr(user, "email", user.get_username()),
                )
            else:
                logger.info(
                    "[로그아웃] 비로그인 요청이 토큰 없이 로그아웃을 시도해 추가 조치 없이 종료했습니다."
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(data={"refresh": refresh_value})
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = RefreshToken(serializer.validated_data["refresh"])
            refresh_token.blacklist()
            logger.info("[로그아웃] Refresh 토큰을 블랙리스트에 등록했습니다.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            logger.warning(
                "[로그아웃] Refresh 토큰 블랙리스트 등록에 실패했습니다.",
                exc_info=True,
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(summary="[인증] 로그인 (토큰 발급)", tags=["Auth & Users"])
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


@extend_schema(summary="[인증] 토큰 갱신", tags=["Auth & Users"])
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
        user.role = "user"  # 역할 변경
        user.save()
        return HttpResponse("이메일 인증이 완료되었습니다.", status=200)
    else:
        return HttpResponse("잘못된 인증 링크입니다.", status=400)


def start_github_oauth(request):
    """GitHub OAuth 인증 흐름을 시작합니다."""

    github_settings = settings.OAUTH_CLIENTS.get("github", {})
    authorize_url = "https://github.com/login/oauth/authorize"
    redirect_uri = _build_github_redirect_uri(request)

    params = {
        "client_id": github_settings.get("client_id"),
        "redirect_uri": redirect_uri,
    }

    scope = github_settings.get("scope")
    if scope:
        params["scope"] = scope

    query = urlencode(
        {key: value for key, value in params.items() if value is not None}
    )
    target_url = f"{authorize_url}?{query}" if query else authorize_url
    return redirect(target_url)


def github_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "missing code"}, status=400)

    # GitHub 토큰 교환 요청
    token_url = "https://github.com/login/oauth/access_token"
    github_settings = settings.OAUTH_CLIENTS.get("github", {})
    redirect_uri = _build_github_redirect_uri(request)
    data = {
        "client_id": github_settings.get("client_id"),
        "client_secret": github_settings.get("client_secret"),
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Accept": "application/json"}
    resp = requests.post(token_url, data=data, headers=headers)
    token_data = resp.json()

    # GitHub 토큰 교환 실패 시 에러 처리
    if "error" in token_data:
        return JsonResponse(token_data, status=400)

    return JsonResponse(token_data)


def github_exchange(request):
    """
    프론트엔드에서 전달받은 code를 기반으로 GitHub 토큰 교환 → 사용자 생성/로그인 처리.
    """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "missing code"}, status=400)

    token_url = "https://github.com/login/oauth/access_token"
    github_settings = settings.OAUTH_CLIENTS.get("github", {})
    redirect_uri = _build_github_redirect_uri(request)
    data = {
        "client_id": github_settings.get("client_id"),
        "client_secret": github_settings.get("client_secret"),
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Accept": "application/json"}
    resp = requests.post(token_url, data=data, headers=headers)
    token_data = resp.json()

    # GitHub 토큰 교환 실패 시 에러 처리
    if "error" in token_data:
        return JsonResponse(token_data, status=400)

    # GitHub 유저 정보 가져오기
    user_info_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token_data.get('access_token')}"},
    )
    if user_info_resp.status_code != 200:
        return JsonResponse(user_info_resp.json(), status=user_info_resp.status_code)
    user_info = user_info_resp.json()

    email = user_info.get("email") or f"{user_info['id']}@github.local"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "nickname": user_info.get("login"),
            "email_verified_at": timezone.now(),
            "role": "user",
        },
    )

    # PATCH: OAuth 교환 시 세션 로그인까지 수행 (세션 기반 화면 루프 방지)
    try:
        login(request, user)  # Django 세션 로그인
    except Exception:
        logger.warning("[GitHub OAuth] 세션 로그인 실패(무시)", exc_info=True)

    # JWT 발급
    refresh = RefreshToken.for_user(user)
    return JsonResponse(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": user.id, "email": user.email, "nickname": user.nickname},
        }
    )


# ============================
# PATCH: 세션 + JWT 겸용 로그아웃 뷰
# ============================
@method_decorator(csrf_protect, name="dispatch")
class CombinedLogoutView(APIView):
    """
    - 세션(OAuth/슈퍼유저/일반) 로그인: Django 세션 종료
    - JWT가 전달되면: Refresh 블랙리스트 시도(실패해도 무해)
    - 항상 성공적으로 종료: XHR이면 JSON 205, 폼이면 /login/으로 리다이렉트
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # 1) JWT 블랙리스트(선택적으로, 실패 무시)
        refresh_value = None
        try:
            refresh_value = (request.data or {}).get("refresh")
        except Exception:
            pass

        if refresh_value:
            try:
                token = RefreshToken(refresh_value)
                try:
                    token.blacklist()
                    logger.info("[CombinedLogout] refresh 블랙리스트 완료")
                except Exception:
                    logger.warning(
                        "[CombinedLogout] 블랙리스트 실패 (무시)", exc_info=True
                    )
            except Exception:
                logger.warning(
                    "[CombinedLogout] refresh 파싱 실패 (무시)", exc_info=True
                )

        # 2) 세션 로그아웃(로그인 안 되어 있어도 무해)
        try:
            if request.user.is_authenticated:
                logger.info(
                    "[CombinedLogout] 세션 사용자 %s 로그아웃",
                    getattr(request.user, "email", request.user.get_username()),
                )
            django_logout(request)
        except Exception:
            logger.warning(
                "[CombinedLogout] 세션 로그아웃 중 예외(무시)", exc_info=True
            )

        # 3) 응답: XHR이면 JSON, 아니면 /login/으로 이동
        wants_json = (
            request.headers.get("Accept", "").startswith("application/json")
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        if wants_json:
            return JsonResponse({"detail": "logged_out"}, status=205)
        return redirect("login-page")
