from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class UserManager(DjangoUserManager):
    # 모든 경로(createsuperuser/Admin 등)에서 이메일 정규화 보장
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email).strip().lower()
        # AbstractUser라 username 필드는 존재(비고유)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=254, verbose_name="이메일")
    username = models.CharField(max_length=100, verbose_name="사용자명")
    nickname = models.CharField(
        max_length=25, blank=True, null=True, verbose_name="닉네임"
    )
    image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="프로필 이미지 URL"
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

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="uq_users_email_ci"),
        ]
        indexes = [
            models.Index(models.F("username"), name="idx_users_username"),
            models.Index(models.F("email"), name="idx_users_email"),
            models.Index(models.F("created_at"), name="idx_users_created_at"),
            # 선택: 부분 인덱스들
            models.Index(
                models.F("created_at"),
                name="idx_users_verified_active",
                condition=Q(is_active=True) & Q(email_verified_at__isnull=False),
            ),
            models.Index(
                models.F("created_at"),
                name="idx_users_unverified",
                condition=Q(email_verified_at__isnull=True),
            ),
            models.Index(
                models.F("phone_number"),
                name="idx_users_phone_present",
                condition=Q(phone_number__isnull=False),
            ),
        ]

    def __str__(self):
        return self.email
