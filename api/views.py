"""API v1 views: JWT auth + CRUD viewsets + public book."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.models import User
from api.permissions import BusinessScopedPermission, IsOwnerOrStaff
from api.serializers import (
    AppointmentSerializer,
    BusinessSerializer,
    CustomerSerializer,
    PublicBookSerializer,
    ServiceSerializer,
    StaffProfileSerializer,
)
from catalog.models import Service
from core.models import Business
from crm.models import Customer
from scheduling.models import Appointment
from staff.models import StaffProfile
from web.utils import get_current_business


# ----- Auth (JWT) -----

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"detail": "E-posta ve şifre gerekli."}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth import authenticate
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"detail": "Geçersiz kimlik bilgileri."}, status=status.HTTP_401_UNAUTHORIZED)
        if user.role not in (User.Role.OWNER, User.Role.STAFF):
            return Response({"detail": "Bu hesap türü API erişimine izinli değil."}, status=status.HTTP_403_FORBIDDEN)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": str(user.id), "email": user.email, "role": user.role},
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        business_name = request.data.get("business_name")
        business_slug = request.data.get("business_slug")
        if not all([email, password, business_name, business_slug]):
            return Response(
                {"detail": "email, password, business_name, business_slug gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Bu e-posta zaten kayıtlı."}, status=status.HTTP_400_BAD_REQUEST)
        if Business.objects.filter(slug=business_slug).exists():
            return Response({"detail": "Bu slug zaten kullanılıyor."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(email=email, password=password, role=User.Role.OWNER)
        business = Business.objects.create(owner=user, name=business_name, slug=business_slug)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": str(user.id), "email": user.email, "role": user.role},
            "business": BusinessSerializer(business).data,
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Optional: blacklist refresh token in production
        return Response({"detail": "Çıkış yapıldı."}, status=status.HTTP_200_OK)


# ----- CRUD ViewSets (business-scoped) -----

class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        business = get_current_business(self.request)
        if not business:
            return Business.objects.none()
        if self.request.user.role == User.Role.OWNER:
            return Business.objects.filter(owner=self.request.user)
        return Business.objects.filter(id=business.id)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["business"] = get_current_business(self.request)
        return ctx


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff, BusinessScopedPermission]

    def get_queryset(self):
        business = get_current_business(self.request)
        if not business:
            return Service.objects.none()
        return Service.objects.filter(business=business)

    def perform_create(self, serializer):
        business = get_current_business(self.request)
        if business:
            serializer.save(business=business)
        else:
            serializer.save()


class StaffProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff, BusinessScopedPermission]

    def get_queryset(self):
        business = get_current_business(self.request)
        if not business:
            return StaffProfile.objects.none()
        return StaffProfile.objects.filter(business=business)

    def perform_create(self, serializer):
        business = get_current_business(self.request)
        if business:
            serializer.save(business=business)
        else:
            serializer.save()


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff, BusinessScopedPermission]

    def get_queryset(self):
        business = get_current_business(self.request)
        if not business:
            return Customer.objects.none()
        return Customer.objects.filter(business=business)

    def perform_create(self, serializer):
        business = get_current_business(self.request)
        if business:
            serializer.save(business=business)
        else:
            serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff, BusinessScopedPermission]

    def get_queryset(self):
        business = get_current_business(self.request)
        if not business:
            return Appointment.objects.none()
        qs = Appointment.objects.filter(business=business).select_related("customer", "service", "staff")
        # Optional filters
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        status_filter = self.request.query_params.get("status")
        staff_id = self.request.query_params.get("staff_id")
        service_id = self.request.query_params.get("service_id")
        if date_from:
            qs = qs.filter(start_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(start_at__date__lte=date_to)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if staff_id:
            qs = qs.filter(staff_id=staff_id)
        if service_id:
            qs = qs.filter(service_id=service_id)
        return qs.order_by("-start_at")

    def perform_create(self, serializer):
        business = get_current_business(self.request)
        if business:
            serializer.save(business=business)
        else:
            serializer.save()


# ----- Public booking (no auth) -----

class PublicBookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PublicBookSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        appointment = ser.save()
        return Response(
            {
                "id": str(appointment.id),
                "start_at": appointment.start_at,
                "end_at": appointment.end_at,
                "status": appointment.status,
                "message": "Randevu oluşturuldu.",
            },
            status=status.HTTP_201_CREATED,
        )
