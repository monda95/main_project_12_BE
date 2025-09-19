from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers

from .utils import normalize_phone

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "username",
            "nickname",
            "image_url",
            "phone_number",
        ]

    def validate_email(self, v):
        v = (v or "").strip().lower()
        if not v:
            raise serializers.ValidationError("이메일은 필수입니다.")
        return v

    def create(self, validated):
        # (선택) 폰넘버 정규화만 아주 가볍게
        if validated.get("phone_number"):
            validated["phone_number"] = normalize_phone(validated["phone_number"])

        try:
            # 핵심 로직(이메일 소문자화/비번 해시)은 Manager가 수행
            return User.objects.create_user(**validated)
        except IntegrityError:
            # DB의 UniqueConstraint(Lower('email')) 위반 시
            raise serializers.ValidationError({"email": "이미 사용 중인 이메일입니다."})


class UserDetailSerializer(serializers.ModelSerializer):
    """
    사용자 상세 정보 조회를 위한 시리얼라이저입니다.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "nickname",
            "image_url",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    사용자 정보(이름, 닉네임, 프로필 이미지, 전화번호) 수정을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "nickname",
            "image_url",
            "phone_number",
        ]  # 추후 실명인증, 휴대폰 인증을 위한 필드추가


class PasswordChangeSerializer(serializers.Serializer):
    """
    비밀번호 변경을 위한 시리얼라이저입니다.
    """

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, min_length=8
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "새 비밀번호가 일치하지 않습니다."}
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class RefreshTokenSerializer(serializers.Serializer):
    """
    로그아웃 시 refresh 토큰을 받기 위한 시리얼라이저입니다.
    """

    refresh = serializers.CharField()


class OAuthBaseSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(
        choices=[(p, p) for p in settings.OAUTH_ALLOWED_PROVIDERS]
    )
    code = serializers.CharField()
    code_verifier = serializers.CharField(required=False, allow_blank=True)
    redirect_uri = serializers.URLField()
    state = serializers.CharField(required=True)  # CSRF 방어를 위한 state 필드 추가


class OAuthExchangeSerializer(OAuthBaseSerializer):
    """인가 코드 교환 → (로그인 or 가입) → JWT 발급"""


class OAuthLinkSerializer(OAuthBaseSerializer):
    """로그인 상태에서 추가 소셜 계정 연결"""


class OAuthAccountSerializer(serializers.Serializer):
    provider = serializers.CharField()
    subject = serializers.CharField()
    email = serializers.EmailField(allow_null=True, required=False)
    email_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField()
