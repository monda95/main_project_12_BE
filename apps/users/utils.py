from typing import Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from .models import OAuthAccount, User


class OAuthError(Exception):
    pass


def exchange_code_for_claims(
    *, provider: str, code: str, code_verifier: str, redirect_uri: str
) -> Dict:
    """
    반드시 반환해야 하는 공통 키:
      - subject (str) : 공급자 사용자 ID
      - email (Optional[str])
      - email_verified (bool)
      - access_token (Optional[str])
      - refresh_token (Optional[str])
      - expires_at (Optional[datetime])
    """
    # --- 아래는 개발 편의를 위한 더미/예시 ---
    # 실제 구현 시 requests로 토큰 교환 → id_token 검증 → userinfo 조회
    if provider not in settings.OAUTH_ALLOWED_PROVIDERS:
        raise OAuthError("provider not allowed")
    # 가짜 응답 스텁
    return {
        "subject": f"stub-{provider}-{code}",
        "email": None,
        "email_verified": False,
        "access_token": None,
        "refresh_token": None,
        "expires_at": None,
    }


def issue_jwt_for_user(user: User) -> Dict[str, str]:
    from rest_framework_simplejwt.tokens import RefreshToken

    rt = RefreshToken.for_user(user)
    return {"access": str(rt.access_token), "refresh": str(rt)}


def complete_oauth_flow(
    *,
    provider: str,
    code: str,
    code_verifier: str,
    redirect_uri: str,
    login_user: Optional[User] = None,
) -> Tuple[User, bool, OAuthAccount]:
    """
    login_user가 None이면: (로그인 or 신규 가입)
    login_user가 있으면: 해당 사용자에 소셜 계정 '연결'
    반환: (최종 User, is_new_user, OAuthAccount)
    """
    claims = exchange_code_for_claims(
        provider=provider,
        code=code,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
    )
    subject = claims["subject"]
    email = (claims.get("email") or "").strip().lower() or None
    email_verified = bool(claims.get("email_verified"))

    # 1) 기존 소셜 연결이 있으면 해당 사용자로 로그인/연결
    try:
        oa = OAuthAccount.objects.select_related("user").get(
            provider=provider, subject=subject
        )
        user = oa.user
        is_new = False
    except OAuthAccount.DoesNotExist:
        if login_user:
            # 2) 연결 모드: 현재 로그인 사용자에 attach
            user = login_user
            is_new = False
        else:
            # 3) 로그인/가입 모드
            if email:
                user = User.objects.filter(email=email).first()
            else:
                user = None

            if not user:
                if not settings.OAUTH_ALLOW_SIGNUP:
                    raise OAuthError("signup disabled")
                # 신규 생성: 이메일이 있으면 세팅(+ provider 검증 신뢰시 verified_at)
                user = User.objects.create_user(
                    email=email or f"{provider}+{subject}@example.local", password=None
                )
                if email and settings.OAUTH_TRUST_PROVIDER_EMAIL and email_verified:
                    user.email_verified_at = timezone.now()
                    user.save(update_fields=["email_verified_at"])
                is_new = True
            else:
                is_new = False

        # OAuthAccount 생성
        oa = OAuthAccount.objects.create(
            user=user,
            provider=provider,
            subject=subject,
            email=email,
            email_verified=email_verified,
            access_token=claims.get("access_token"),
            refresh_token=claims.get("refresh_token"),
            token_expires_at=claims.get("expires_at"),
        )

    return user, is_new, oa
