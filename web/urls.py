from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("pricing/", views.pricing, name="pricing"),
    path("companies/", views.business_list, name="business_list"),
    path("auth/login/", views.auth_login, name="login"),
    path("auth/logout/", views.auth_logout, name="logout"),
    path("auth/register/", views.auth_register, name="register"),
    path("auth/forgot/", views.auth_forgot, name="forgot"),
    path("b/<slug:business_slug>/", views.public_booking, name="booking"),
    path("legal/terms/", views.legal_terms, name="terms"),
    path("legal/privacy/", views.legal_privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
    # Dashboard
    path("app/", views.dashboard, name="dashboard"),
    path("app/calendar/", views.app_calendar, name="app_calendar"),
    path("app/appointments/", views.app_appointments, name="app_appointments"),
    path("app/customers/", views.app_customers, name="app_customers"),
    path("app/customers/<uuid:uuid>/", views.app_customer_detail, name="app_customer_detail"),
    path("app/services/", views.app_services, name="app_services"),
    path("app/staff/", views.app_staff, name="app_staff"),
    path("app/settings/", views.app_settings, name="app_settings"),
    path("app/billing/", views.app_billing, name="app_billing"),
    path("app/notifications/", views.app_notifications, name="app_notifications"),
    path("app/help/", views.app_help, name="app_help"),
]
