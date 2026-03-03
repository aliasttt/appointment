import uuid

from django.db import models

from catalog.models import Service
from core.models import Business
from crm.models import Customer
from staff.models import StaffProfile


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Beklemede"
        CONFIRMED = "CONFIRMED", "Onaylandı"
        COMPLETED = "COMPLETED", "Tamamlandı"
        CANCELED = "CANCELED", "İptal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        related_name="appointments",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    start_at = models.DateTimeField("Başlangıç")
    end_at = models.DateTimeField("Bitiş")
    status = models.CharField(
        "Durum",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField("Notlar", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Randevu"
        verbose_name_plural = "Randevular"
        ordering = ["-start_at"]

    def __str__(self) -> str:
        return f"{self.business.name} - {self.customer.name} - {self.start_at}"
