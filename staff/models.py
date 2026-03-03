import uuid

from django.conf import settings
from django.db import models

from core.models import Business


class StaffProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="staff",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    name = models.CharField("Ad soyad", max_length=255)
    phone = models.CharField("Telefon", max_length=20, blank=True)
    specialties = models.CharField("Uzmanlıklar", max_length=255, blank=True)
    working_hours = models.JSONField("Çalışma saatleri", default=dict, blank=True)

    class Meta:
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"

    def __str__(self) -> str:
        return self.name
