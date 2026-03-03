from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "duration_min", "price_try", "active")
    list_filter = ("active", "business")
    search_fields = ("name",)
    raw_id_fields = ("business",)
