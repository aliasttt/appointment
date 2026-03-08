import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Kullanıcıların bir e-posta adresi olmalıdır.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "SUPERADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Süper kullanıcı is_staff=True olmalıdır.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Süper kullanıcı is_superuser=True olmalıdır.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Süper Admin"
        OWNER = "OWNER", "İşletme Sahibi"
        STAFF = "STAFF", "Personel"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField("E-posta", unique=True)
    # Override inherited field labels so admin shows clear Turkish text (not "Görev durumu")
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Admin panele giriş",
        help_text="Bu kullanıcının /admin/ sitesine oturum açıp açamayacağını belirler. Yalnızca süper admin için işaretli olmalı.",
    )
    phone = models.CharField(
        "Telefon",
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="İşletme sahibi için benzersiz olmalıdır.",
    )
    role = models.CharField(
        "Rol",
        max_length=20,
        choices=Role.choices,
        default=Role.OWNER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
