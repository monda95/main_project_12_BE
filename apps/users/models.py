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
    email = models.EmailField(max_length=254)  # unique=False
    username = models.CharField(max_length=100)
    nickname = models.CharField(max_length=25, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 로그인 식별자 = email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
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
