"""Helpers for web views: current business resolution."""

from accounts.models import User
from core.models import Business


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
