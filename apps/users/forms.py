from django import forms
from django.contrib.auth import get_user_model

from .utils import normalize_phone

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "nickname", "image_url", "phone_number"]

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not phone:
            return phone
        try:
            return normalize_phone(phone)
        except ValueError as e:
            raise forms.ValidationError(str(e))
