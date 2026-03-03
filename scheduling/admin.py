from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("business", "customer", "service", "staff", "start_at", "status")
    list_filter = ("status", "business")
    search_fields = ("customer__name", "notes")
    raw_id_fields = ("business", "customer", "service", "staff")
    date_hierarchy = "start_at"
