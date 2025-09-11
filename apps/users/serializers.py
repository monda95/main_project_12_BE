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
        return v.strip().lower()

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
