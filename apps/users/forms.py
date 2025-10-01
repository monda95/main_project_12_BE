from django import forms


class SignupForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(
        label="비밀번호", widget=forms.PasswordInput, min_length=8
    )
    password_confirm = forms.CharField(
        label="비밀번호 확인", widget=forms.PasswordInput, min_length=8
    )
    nickname = forms.CharField(label="닉네임", required=False, max_length=50)

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

        email = self.cleaned_data["email"]
        username = (self.cleaned_data.get("nickname") or "").strip() or email.split("@")[0]

        payload = {
            "email": email,
            "password": self.cleaned_data["password"],
            "username": username,
        }

        nickname = (self.cleaned_data.get("nickname") or "").strip()
        if nickname:
            payload["nickname"] = nickname

        return payload
