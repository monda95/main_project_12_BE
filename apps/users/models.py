from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class UserManager(DjangoUserManager):
    """모든 생성 경로에서 이메일을 소문자로 정규화합니다."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    - 로그인 식별자는 email 입니다(USERNAME_FIELD='email')
    - 이메일은 항상 소문자로 저장되며(DB CheckConstraint), DB 레벨 unique 로 보장
    - 고유키는 email 하나로만 유지
    """

    # AbstractUser의 username 필드는 그대로 사용(필요시 unique 완화는 별도 마이그레이션에서 처리)
    email = models.EmailField(unique=True, max_length=254, verbose_name="이메일")
    username = models.CharField(max_length=100, unique=False, verbose_name="사용자명")
    nickname = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="닉네임"
    )
    image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="프로필 이미지"
    )
    phone_number = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="전화번호"
    )

    email_verified_at = models.DateTimeField(
        blank=True, null=True, verbose_name="이메일 인증 시각"
    )
    deactivated_at = models.DateTimeField(
        blank=True, null=True, verbose_name="탈퇴일시"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 시각")

    # 로그인 식별자 = email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"

        # 저장값 항상 소문자 DB 레벨에서 강제
        constraints = [
            models.CheckConstraint(
                name="users_email_is_lower",
                condition=Q(email=Lower("email")),
            ),
        ]

        indexes = [
            models.Index(fields=["created_at"], name="idx_users_created_at"),
            models.Index(
                fields=["deactivated_at"],
                name="idx_users_deactivated_nonnull",
                condition=Q(deactivated_at__isnull=False),
            ),
        ]

    def save(self, *args, **kwargs):
        # 방어적 정규화(시리얼라이저/매니저에서 이미 처리하지만, 이중화하여 안전)
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class OAuthAccount(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google", "구글"
        GITHUB = "github", "깃허브"
        KAKAO = "kakao", "카카오"
        NAVER = "naver", "네이버"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oauth_accounts",
        verbose_name="사용자",
    )
    provider = models.CharField(
        max_length=30, choices=Provider.choices, verbose_name="공급자"
    )
    subject = models.CharField(max_length=191, verbose_name="공급자 사용자 식별자(sub)")
    email = models.EmailField(blank=True, null=True, verbose_name="공급자 이메일")
    email_verified = models.BooleanField(
        default=False, verbose_name="공급자 이메일 인증 여부"
    )

    # 토큰 저장은 선택(필요 시만). 운영에선 암호화/만료/회전 정책 고려 권장.
    access_token = models.TextField(blank=True, null=True, verbose_name="액세스 토큰")
    refresh_token = models.TextField(
        blank=True, null=True, verbose_name="리프레시 토큰"
    )
    token_expires_at = models.DateTimeField(
        blank=True, null=True, verbose_name="토큰 만료 시각"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")

    class Meta:
        db_table = "oauth_accounts"
        verbose_name = "소셜 계정"
        verbose_name_plural = "소셜 계정 목록"
        # 고유/체크 제약
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "subject"],
                name="uq_oauth_provider_subject",
            ),
            models.CheckConstraint(
                check=Q(provider__in=["google", "github", "kakao", "naver"]),
                name="chk_oauth_provider",
            ),  # 참조 오류가 귀찮아서, for, lambda 방식보다 직접 적어넣는 하드코딩으로 쉽지만 유지보수는 더 귀찮은 길을 채택
        ]
        # 조회/정렬 실사용 인덱스
        indexes = [
            models.Index(fields=["user"], name="idx_oauth_user"),
            models.Index(fields=["created_at"], name="idx_oauth_created"),
        ]

    def __str__(self):
        return f"{self.provider}:{self.subject} -> {self.user_id}"
