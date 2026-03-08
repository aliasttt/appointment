"""Form for Django admin User: unique email and phone validation with clear error messages."""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import User


class UserAdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "phone", "role")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("قبلاً کاربری با این ایمیل ثبت‌نام کرده است.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone") or None
        if phone and User.objects.filter(phone=phone).exists():
            raise ValidationError("قبلاً کاربری با این شماره تلفن ثبت‌نام کرده است.")
        return phone


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("قبلاً کاربری با این ایمیل ثبت‌نام کرده است.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone") or None
        if not phone:
            return phone
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("قبلاً کاربری با این شماره تلفن ثبت‌نام کرده است.")
        return phone
