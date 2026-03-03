from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "business", "created_at")
    list_filter = ("business",)
    search_fields = ("name", "phone")
    raw_id_fields = ("business",)
