"""API v1 serializers."""

from rest_framework import serializers

from accounts.models import User
from catalog.models import Service
from core.models import Business
from crm.models import Customer
from scheduling.models import Appointment
from staff.models import StaffProfile


class UserMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role")


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "phone",
            "address",
            "payment_status",
            "trial_ends_at",
            "working_hours",
            "booking_settings",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "payment_status", "trial_ends_at", "created_at", "updated_at")


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "name", "duration_min", "price_try", "active")
        read_only_fields = ("id",)


class StaffProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = StaffProfile
        fields = ("id", "user", "user_email", "name", "phone", "specialties", "working_hours")
        read_only_fields = ("id",)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name", "phone", "notes", "created_at")
        read_only_fields = ("id", "created_at")


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)
    staff_name = serializers.CharField(source="staff.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "customer",
            "customer_name",
            "service",
            "service_name",
            "staff",
            "staff_name",
            "start_at",
            "end_at",
            "status",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class PublicBookSerializer(serializers.Serializer):
    business_slug = serializers.SlugField()
    service_id = serializers.UUIDField()
    staff_id = serializers.UUIDField(required=False, allow_null=True)
    date = serializers.DateField()
    time = serializers.TimeField()
    customer_name = serializers.CharField(max_length=255)
    customer_phone = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_business_slug(self, value):
        if not Business.objects.filter(slug=value).exists():
            raise serializers.ValidationError("İşletme bulunamadı.")
        return value

    def validate_service_id(self, value):
        business_slug = self.initial_data.get("business_slug")
        if not business_slug:
            return value
        if not Service.objects.filter(business__slug=business_slug, id=value, active=True).exists():
            raise serializers.ValidationError("Geçersiz veya pasif hizmet.")
        return value

    def validate_staff_id(self, value):
        if value is None:
            return value
        business_slug = self.initial_data.get("business_slug")
        if not business_slug:
            return value
        if not StaffProfile.objects.filter(business__slug=business_slug, id=value).exists():
            raise serializers.ValidationError("Geçersiz personel.")
        return value

    def create(self, validated_data):
        from django.utils import timezone

        business = Business.objects.get(slug=validated_data["business_slug"])
        service = Service.objects.get(business=business, id=validated_data["service_id"])
        staff = None
        if validated_data.get("staff_id"):
            staff = StaffProfile.objects.get(business=business, id=validated_data["staff_id"])

        start_at = timezone.make_aware(
            timezone.datetime.combine(validated_data["date"], validated_data["time"])
        )
        from datetime import timedelta
        end_at = start_at + timedelta(minutes=service.duration_min)

        customer, _ = Customer.objects.get_or_create(
            business=business,
            phone=validated_data["customer_phone"],
            defaults={"name": validated_data["customer_name"], "notes": validated_data.get("notes", "")},
        )
        if not customer.name or customer.name != validated_data["customer_name"]:
            customer.name = validated_data["customer_name"]
            customer.save(update_fields=["name"])

        appointment = Appointment.objects.create(
            business=business,
            customer=customer,
            service=service,
            staff=staff,
            start_at=start_at,
            end_at=end_at,
            status=Appointment.Status.PENDING,
            notes=validated_data.get("notes", ""),
        )
        return appointment
