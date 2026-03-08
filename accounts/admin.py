from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms_admin import UserAdminChangeForm, UserAdminCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ("email", "phone", "role", "get_payment_status", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "phone")
    ordering = ("email",)
    readonly_fields = ("get_payment_status_readonly",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Kişisel"), {"fields": ("phone", "role")}),
        (_("Ödeme (İşletme)"), {"fields": ("get_payment_status_readonly",), "description": "İşletme sahibi ise işletmenin ödeme durumu."}),
        (_("İzinler"), {"fields": ("is_staff", "is_active", "is_superuser")}),
    )

    def get_payment_status(self, obj):
        biz = getattr(obj, "businesses", None)
        if biz is None:
            return "—"
        first = biz.first()
        if not first:
            return "—"
        return first.get_payment_status_display()

    get_payment_status.short_description = "Ödeme durumu"

    def get_payment_status_readonly(self, obj):
        if not obj.pk:
            return "—"
        return self.get_payment_status(obj)

    get_payment_status_readonly.short_description = "Ödeme durumu"
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone", "password1", "password2", "role"),
            },
        ),
    )

