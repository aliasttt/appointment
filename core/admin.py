from django.contrib import admin
from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "phone", "payment_status", "trial_ends_at", "created_at")
    list_editable = ("payment_status",)
    list_filter = ("payment_status", "created_at")
    search_fields = ("name", "slug", "phone", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("owner",)
