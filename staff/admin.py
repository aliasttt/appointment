from django.contrib import admin
from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "business", "phone")
    list_filter = ("business",)
    search_fields = ("name", "user__email")
    raw_id_fields = ("business", "user")
