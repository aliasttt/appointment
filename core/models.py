import uuid

from django.conf import settings
from django.db import models


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businesses",
    )
    name = models.CharField("İşletme adı", max_length=255)
    slug = models.SlugField("Slug", unique=True)
    phone = models.CharField("Telefon", max_length=20, blank=True)
    address = models.TextField("Adres", blank=True)
    working_hours = models.JSONField("Çalışma saatleri", default=dict, blank=True)
    booking_settings = models.JSONField("Randevu ayarları", default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "İşletme"
        verbose_name_plural = "İşletmeler"

    def __str__(self) -> str:
        return self.name
