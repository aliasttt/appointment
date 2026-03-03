import uuid

from django.db import models

from core.models import Business


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="services",
    )
    name = models.CharField("Hizmet adı", max_length=255)
    duration_min = models.PositiveIntegerField("Süre (dakika)")
    price_try = models.DecimalField("Fiyat (₺)", max_digits=10, decimal_places=2)
    active = models.BooleanField("Aktif", default=True)

    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"

    def __str__(self) -> str:
        return self.name
