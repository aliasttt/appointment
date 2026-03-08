"""Helpers for web views: current business resolution and public booking slots."""

from datetime import time, timedelta

from django.utils import timezone

from accounts.models import User
from core.models import Business
from scheduling.models import Appointment


def get_current_business(request):
    """
    Return the business for the current user (owner's first business or staff's business).
    Returns None if user has no business context.
    """
    user = request.user
    if not user.is_authenticated:
        return None
    if user.role == User.Role.OWNER:
        return user.businesses.first()
    if user.role == User.Role.STAFF and hasattr(user, "staff_profile"):
        return user.staff_profile.business
    return None


def get_working_hours_for_weekday(business, weekday):
    """
    weekday: 0=Monday, 6=Sunday.
    Returns (start_time, end_time) as time objects, or default (9:00, 18:00).
    working_hours format: {"0": ["09:00", "18:00"], "1": ["09:00", "18:00"], ...}
    """
    wh = getattr(business, "working_hours", None) or {}
    key = str(weekday)
    val = wh.get(key)
    if not isinstance(val, (list, tuple)) or len(val) < 2:
        return (time(9, 0), time(18, 0))
    try:
        start = time.fromisoformat(val[0])
        end = time.fromisoformat(val[1])
        return (start, end)
    except (TypeError, ValueError):
        return (time(9, 0), time(18, 0))


def get_available_times(business, date, slot_minutes=30):
    """
    Return list of (time, "HH:MM") for the given date that don't overlap existing appointments.
    """
    if date < timezone.now().date():
        return []
    weekday = date.weekday()
    start_t, end_t = get_working_hours_for_weekday(business, weekday)
    slots = []
    current = timezone.datetime.combine(date, start_t)
    end_dt = timezone.datetime.combine(date, end_t)
    while current + timedelta(minutes=slot_minutes) <= end_dt:
        slots.append(current.time())
        current += timedelta(minutes=slot_minutes)
    if not slots:
        return []

    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(timezone.datetime.combine(date, time(0, 0)), tz)
    day_end = day_start + timedelta(days=1)
    existing = list(
        business.appointments.filter(
            start_at__lt=day_end,
            end_at__gt=day_start,
        ).exclude(status=Appointment.Status.CANCELED).values_list("start_at", "end_at")
    )

    result = []
    for t in slots:
        slot_start = timezone.make_aware(timezone.datetime.combine(date, t), tz)
        slot_end = slot_start + timedelta(minutes=slot_minutes)
        if slot_end <= timezone.now():
            continue
        overlap = any(slot_start < e and slot_end > s for s, e in existing)
        if not overlap:
            result.append((t, t.strftime("%H:%M")))
    return result


def get_next_booking_dates(count=14):
    """Return next `count` dates (including today) for date picker."""
    today = timezone.now().date()
    return [today + timedelta(days=i) for i in range(count)]
