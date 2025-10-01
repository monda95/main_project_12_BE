import requests
from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.http import JsonResponse
from django.conf import settings

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


class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        return email.strip().lower()


class SignupForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput, min_length=8
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인", widget=forms.PasswordInput, min_length=8
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "비밀번호가 일치하지 않습니다.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        username = email
        return User.objects.create_user(
            email=email,
            password=password,
            username=username,
        )


class LoginPageView(View):
    template_name = "login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is None:
                form.add_error(None, "이메일 또는 비밀번호가 올바르지 않습니다.")
            elif not user.is_active:
                form.add_error(None, "비활성화된 계정입니다. 관리자에게 문의하세요.")
            elif (
                getattr(settings, "AUTH_EMAIL_VERIFICATION_REQUIRED", False)
                and not getattr(user, "email_verified_at", None)
            ):
                form.add_error(None, "이메일 인증이 필요합니다.")
            else:
                login(request, user)
                return redirect("dashboard-page")
        return render(request, self.template_name, {"form": form})


class SignupPageView(View):
    template_name = "signup.html"
    form_class = SignupForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error("email", "이미 사용 중인 이메일입니다.")
            else:
                return redirect("login-page")
        return render(request, self.template_name, {"form": form})


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


def github_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "missing code"}, status=400)

    # GitHub 토큰 교환 요청
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": settings.OAUTH_CLIENTS["github"]["client_id"],
        "client_secret": settings.OAUTH_CLIENTS["github"]["client_secret"],
        "code": code,
        "redirect_uri": settings.OAUTH_CLIENTS["github"]["redirect_uri"],
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
    data = {
        "client_id": settings.OAUTH_CLIENTS["github"]["client_id"],
        "client_secret": settings.OAUTH_CLIENTS["github"]["client_secret"],
        "code": code,
        "redirect_uri": settings.OAUTH_CLIENTS["github"]["redirect_uri"],
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

    # JWT 발급
    refresh = RefreshToken.for_user(user)
    return JsonResponse(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": user.id, "email": user.email, "nickname": user.nickname},
        }
    )
