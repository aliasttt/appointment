"""Seed demo data: owner, staff, business, services, customers, appointments."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from catalog.models import Service
from core.models import Business
from crm.models import Customer
from scheduling.models import Appointment
from staff.models import StaffProfile


DEMO_PASSWORD = "Demo12345!"


class Command(BaseCommand):
    help = "Create demo owner, staff, business, services, customers and a week of appointments."

    def add_arguments(self, parser):
        parser.add_argument("--no-input", action="store_true", help="Do not prompt; overwrite if exists.")

    def handle(self, *args, **options):
        no_input = options["no_input"]
        now = timezone.now()

        owner, owner_created = User.objects.get_or_create(
            email="owner@randevupro.com",
            defaults={"role": User.Role.OWNER},
        )
        if owner_created:
            owner.set_password(DEMO_PASSWORD)
            owner.save()
            self.stdout.write(self.style.SUCCESS("Demo owner created: owner@randevupro.com"))
        else:
            owner.set_password(DEMO_PASSWORD)
            owner.save()
            self.stdout.write("Demo owner already exists; password reset to Demo12345!")

        staff_user, staff_user_created = User.objects.get_or_create(
            email="staff@randevupro.com",
            defaults={"role": User.Role.STAFF},
        )
        if staff_user_created:
            staff_user.set_password(DEMO_PASSWORD)
            staff_user.save()
            self.stdout.write(self.style.SUCCESS("Demo staff user created: staff@randevupro.com"))

        business, business_created = Business.objects.get_or_create(
            slug="demo-salon",
            defaults={
                "owner": owner,
                "name": "Demo Kuaför Salonu",
                "phone": "+90 212 555 0000",
                "address": "İstanbul, Türkiye",
            },
        )
        if business_created:
            self.stdout.write("Demo business created: Demo Kuaför Salonu (slug: demo-salon)")

        if staff_user_created or not StaffProfile.objects.filter(business=business, user=staff_user).exists():
            StaffProfile.objects.get_or_create(
                business=business,
                user=staff_user,
                defaults={"name": "Ayşe Yılmaz", "phone": "+90 532 111 2233", "specialties": "Saç kesimi, Boya"},
            )
            if not staff_user_created:
                staff_user.set_password(DEMO_PASSWORD)
                staff_user.save()
            self.stdout.write("Demo staff profile linked.")

        services_data = [
            ("Saç Kesimi", 30, 150),
            ("Sakal Tıraşı", 15, 50),
            ("Saç Boyama", 90, 350),
        ]
        for name, duration_min, price_try in services_data:
            Service.objects.get_or_create(
                business=business,
                name=name,
                defaults={"duration_min": duration_min, "price_try": price_try, "active": True},
            )
        self.stdout.write(f"Services: {Service.objects.filter(business=business).count()}")

        customers_data = [
            ("Mehmet Demir", "+90 532 111 0001"),
            ("Zeynep Kaya", "+90 532 111 0002"),
            ("Ali Öz", "+90 532 111 0003"),
        ]
        customers = []
        for name, phone in customers_data:
            c, _ = Customer.objects.get_or_create(
                business=business,
                phone=phone,
                defaults={"name": name},
            )
            if c.name != name:
                c.name = name
                c.save()
            customers.append(c)
        self.stdout.write(f"Customers: {len(customers)}")

        staff_profile = business.staff.first()
        service_list = list(business.services.all())
        if not service_list:
            self.stdout.write(self.style.WARNING("No services; skipping appointments."))
        else:
            base_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if base_date < now:
                base_date += timedelta(days=1)
            created = 0
            for day_offset in range(7):
                day = base_date + timedelta(days=day_offset)
                for slot in range(4):
                    start = day + timedelta(hours=slot * 2)
                    if start < now:
                        continue
                    customer = customers[slot % len(customers)]
                    service = service_list[slot % len(service_list)]
                    end = start + timedelta(minutes=service.duration_min)
                    _, apt_created = Appointment.objects.get_or_create(
                        business=business,
                        start_at=start,
                        customer=customer,
                        defaults={
                            "service": service,
                            "staff": staff_profile,
                            "end_at": end,
                            "status": Appointment.Status.CONFIRMED if day_offset < 2 else Appointment.Status.PENDING,
                        },
                    )
                    if apt_created:
                        created += 1
            self.stdout.write(self.style.SUCCESS(f"Appointments created: {created}"))

        self.stdout.write(self.style.SUCCESS("\nDemo login (web):"))
        self.stdout.write("  Owner: owner@randevupro.com / Demo12345!")
        self.stdout.write("  Staff: staff@randevupro.com / Demo12345!")
        self.stdout.write("  Public booking: /b/demo-salon/")
