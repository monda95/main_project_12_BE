from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput, strip=False
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        return email


class SignupForm(forms.Form):
    email = forms.EmailField(
        label="이메일",
        error_messages={"required": "email은 필수입니다."},
    )
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput, min_length=8
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인", widget=forms.PasswordInput, min_length=8
    )
    username = forms.CharField(
        label="사용자명",
        max_length=100,
        error_messages={"required": "사용자명은 필수입니다."},
    )
    nickname = forms.CharField(label="닉네임", required=False, max_length=50)
    image_url = forms.URLField(
        label="프로필 이미지 URL", required=False, max_length=500
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "비밀번호가 일치하지 않습니다.")
        return cleaned_data

    def build_serializer_payload(self):
        if not hasattr(self, "cleaned_data"):
            raise ValueError("유효한 폼 데이터가 필요합니다.")

        payload = {
            "email": self.cleaned_data["email"],
            "password": self.cleaned_data["password"],
            "username": self.cleaned_data["username"],
        }

        optional_fields = ["nickname", "image_url"]
        for field in optional_fields:
            payload[field] = self.cleaned_data.get(field)

        return payload
