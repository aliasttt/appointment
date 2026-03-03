"""Forms for auth (login, register, forgot password)."""

from django import forms
from django.contrib.auth import authenticate, get_user_model

from core.models import Business

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "ornek@email.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("E-posta veya şifre hatalı.")
            data["user"] = user
        return data


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "ornek@email.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label="Şifre (tekrar)",
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "new-password"}),
    )
    business_name = forms.CharField(
        label="İşletme adı",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Salon Adı"}),
    )
    business_slug = forms.SlugField(
        label="Randevu sayfası adresi (slug)",
        max_length=64,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "salon-adi"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean_password_confirm(self):
        if self.cleaned_data.get("password") != self.cleaned_data.get("password_confirm"):
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return self.cleaned_data["password_confirm"]

    def clean_business_slug(self):
        slug = self.cleaned_data.get("business_slug")
        if slug and Business.objects.filter(slug=slug).exists():
            raise forms.ValidationError("Bu adres zaten kullanılıyor.")
        return slug


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="E-posta",
        widget=forms.EmailInput(attrs={"class": "input", "placeholder": "ornek@email.com", "autocomplete": "email"}),
    )
