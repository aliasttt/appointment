"""Web (server-rendered) views: public pages + dashboard."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.forms import ForgotPasswordForm, LoginForm, RegisterForm
from accounts.models import User
from catalog.models import Service
from core.models import Business
from crm.models import Customer
from scheduling.models import Appointment
from staff.models import StaffProfile
from django.utils import timezone
from datetime import timedelta

from web.utils import get_current_business, get_available_times, get_next_booking_dates, can_access_app


# ----- Public -----

def home(request):
    return render(request, "web/home.html")


def pricing(request):
    return render(request, "web/pricing.html")


def business_list(request):
    """List all businesses; users can open each one's booking page to request an appointment."""
    businesses = Business.objects.prefetch_related("services").order_by("name")
    return render(request, "web/business_list.html", {"businesses": businesses})


@require_http_methods(["GET", "POST"])
def auth_login(request):
    if request.user.is_authenticated:
        return redirect("web:dashboard")
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        next_url = request.GET.get("next") or reverse("web:dashboard")
        return redirect(next_url)
    return render(request, "web/auth/login.html", {"form": form})


def auth_logout(request):
    logout(request)
    return redirect("web:login")


@require_http_methods(["GET", "POST"])
def auth_register(request):
    if request.user.is_authenticated:
        return redirect("web:dashboard")
    form = RegisterForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            role=User.Role.OWNER,
        )
        trial_ends = timezone.now() + timedelta(days=7)
        business = Business.objects.create(
            owner=user,
            name=form.cleaned_data["business_name"],
            slug=form.cleaned_data["business_slug"],
            phone=form.cleaned_data.get("phone", ""),
            address=form.cleaned_data.get("address", ""),
            trial_ends_at=trial_ends,
        )
        login(request, user)
        messages.success(request, "Hesabınız oluşturuldu. 7 gün ücretsiz deneme süreniz başladı.")
        return redirect("web:dashboard")
    return render(request, "web/auth/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def auth_forgot(request):
    form = ForgotPasswordForm(data=request.POST or None)
    sent = False
    if request.method == "POST" and form.is_valid():
        # Stub: in production send email with reset link
        sent = True
        messages.success(request, "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi (demo: gönderilmedi).")
    return render(request, "web/auth/forgot.html", {"form": form, "sent": sent})


def public_booking(request, business_slug):
    business = get_object_or_404(Business, slug=business_slug)
    services = business.services.filter(active=True)
    staff_list = business.staff.all()
    dates = get_next_booking_dates(14)
    return render(request, "web/booking.html", {
        "business": business,
        "services": services,
        "staff_list": staff_list,
        "dates": dates,
    })


def public_booking_slots(request, business_slug):
    """HTMX: return HTML fragment of time slot buttons for a given date."""
    business = get_object_or_404(Business, slug=business_slug)
    date_str = request.GET.get("date")
    if not date_str:
        return render(request, "web/booking_slots_fragment.html", {"slots": []})
    from datetime import datetime
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "web/booking_slots_fragment.html", {"slots": []})
    slots = get_available_times(business, day)
    return render(request, "web/booking_slots_fragment.html", {"slots": slots, "date": date_str})


@require_http_methods(["POST"])
def public_booking_submit(request, business_slug):
    """Handle public booking form submit; no login required."""
    business = get_object_or_404(Business, slug=business_slug)
    from api.serializers import PublicBookSerializer
    payload = {
        "business_slug": business_slug,
        "service_id": request.POST.get("service_id"),
        "staff_id": request.POST.get("staff_id") or None,
        "date": request.POST.get("date"),
        "time": request.POST.get("time"),
        "customer_name": request.POST.get("customer_name", "").strip(),
        "customer_phone": request.POST.get("customer_phone", "").strip(),
        "notes": request.POST.get("notes", "").strip() or "",
    }
    ser = PublicBookSerializer(data=payload)
    if not ser.is_valid():
        for field, err in ser.errors.items():
            msg = err[0] if isinstance(err, list) else str(err)
            messages.error(request, msg)
        return redirect("web:booking", business_slug=business_slug)
    ser.save()
    messages.success(request, "Randevunuz alındı. İşletme sizinle iletişime geçebilir.")
    return redirect("web:booking", business_slug=business_slug)


def legal_terms(request):
    return render(request, "web/legal/terms.html")


def legal_privacy(request):
    return render(request, "web/legal/privacy.html")


def contact(request):
    return render(request, "web/contact.html")


# ----- Dashboard (login required, business context) -----

def _require_business(view_func):
    """Decorator: redirect to dashboard if no business (e.g. owner with no business)."""
    def wrapper(request, *args, **kwargs):
        business = get_current_business(request)
        if not business:
            messages.warning(request, "Henüz bir işletme tanımlı değil.")
            return redirect("web:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def _require_active_subscription(view_func):
    """Decorator: redirect to billing if trial ended and payment not PAID (access only after trial or paid)."""
    def wrapper(request, *args, **kwargs):
        business = get_current_business(request)
        if business and not can_access_app(business):
            messages.warning(
                request,
                "Deneme süreniz bitti. Devam etmek için ödemenizi yapıp yönetici onayı bekleyin (WhatsApp ile iletişime geçin).",
            )
            return redirect("web:billing")
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    business = get_current_business(request)
    if not business:
        return render(request, "web/dashboard/dashboard.html", {"business": None})
    if not can_access_app(business):
        messages.warning(
            request,
            "Deneme süreniz bitti. Devam etmek için ödemenizi yapıp yönetici onayı bekleyin (WhatsApp ile iletişime geçin).",
        )
        return redirect("web:billing")
    now = timezone.now()
    upcoming = business.appointments.filter(start_at__gte=now).exclude(status=Appointment.Status.CANCELED).order_by("start_at")[:10]
    total_appointments = business.appointments.count()
    total_customers = business.customers.count()
    return render(request, "web/dashboard/dashboard.html", {
        "business": business,
        "upcoming": upcoming,
        "total_appointments": total_appointments,
        "total_customers": total_customers,
    })


@login_required
@_require_business
@_require_active_subscription
def app_calendar(request):
    business = get_current_business(request)
    return render(request, "web/dashboard/calendar.html", {"business": business})


@login_required
@_require_business
@_require_active_subscription
def app_appointments(request):
    business = get_current_business(request)
    appointments = business.appointments.select_related("customer", "service", "staff").order_by("-start_at")[:100]
    return render(request, "web/dashboard/appointments.html", {"business": business, "appointments": appointments})


@login_required
@_require_business
@_require_active_subscription
def app_customers(request):
    business = get_current_business(request)
    customers = business.customers.order_by("-created_at")[:100]
    return render(request, "web/dashboard/customers.html", {"business": business, "customers": customers})


@login_required
@_require_business
@_require_active_subscription
def app_customer_detail(request, uuid):
    business = get_current_business(request)
    customer = get_object_or_404(Customer, business=business, id=uuid)
    visits = customer.appointments.select_related("service", "staff").order_by("-start_at")
    return render(request, "web/dashboard/customer_detail.html", {"business": business, "customer": customer, "visits": visits})


@login_required
@_require_business
@_require_active_subscription
def app_services(request):
    business = get_current_business(request)
    services = business.services.all()
    return render(request, "web/dashboard/services.html", {"business": business, "services": services})


@login_required
@_require_business
@_require_active_subscription
def app_staff(request):
    business = get_current_business(request)
    staff_list = business.staff.select_related("user").all()
    return render(request, "web/dashboard/staff.html", {"business": business, "staff_list": staff_list})


@login_required
@_require_business
@_require_active_subscription
def app_settings(request):
    business = get_current_business(request)
    return render(request, "web/dashboard/settings.html", {"business": business})


@login_required
@_require_business
def app_billing(request):
    business = get_current_business(request)
    return render(request, "web/dashboard/billing.html", {"business": business})


@login_required
@_require_business
@_require_active_subscription
def app_notifications(request):
    business = get_current_business(request)
    return render(request, "web/dashboard/notifications.html", {"business": business})


@login_required
@_require_business
@_require_active_subscription
def app_help(request):
    business = get_current_business(request)
    return render(request, "web/dashboard/help.html", {"business": business})
