from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    AppointmentViewSet,
    BusinessViewSet,
    CustomerViewSet,
    LoginView,
    LogoutView,
    PublicBookView,
    RegisterView,
    ServiceViewSet,
    StaffProfileViewSet,
)

router = DefaultRouter()
router.register("business", BusinessViewSet, basename="business")
router.register("services", ServiceViewSet, basename="service")
router.register("staff", StaffProfileViewSet, basename="staff")
router.register("customers", CustomerViewSet, basename="customer")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="api_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_refresh"),
    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("auth/logout/", LogoutView.as_view(), name="api_logout"),
    path("public/book/", PublicBookView.as_view(), name="api_public_book"),
    path("", include(router.urls)),
]
