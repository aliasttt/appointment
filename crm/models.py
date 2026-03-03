import uuid

from django.db import models

from core.models import Business


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="customers",
    )
    name = models.CharField("Ad soyad", max_length=255)
    phone = models.CharField("Telefon", max_length=20)
    notes = models.TextField("Notlar", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"

    def __str__(self) -> str:
        return f"{self.name} ({self.phone})"
