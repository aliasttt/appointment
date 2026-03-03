"""API permissions: business-scoped access for Owner and Staff."""

from rest_framework import permissions

from accounts.models import User
from web.utils import get_current_business


def get_business_from_request(request):
    """Return business for API request (user must be authenticated)."""
    return get_current_business(request)


class IsOwnerOrStaff(permissions.BasePermission):
    """Allow only OWNER or STAFF; optionally require business context."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role not in (User.Role.OWNER, User.Role.STAFF):
            return False
        return True


class BusinessScopedPermission(permissions.BasePermission):
    """
    Object-level: user can only access objects belonging to their business.
    Use with views that have get_queryset() filtering by business.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role not in (User.Role.OWNER, User.Role.STAFF):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        business = get_business_from_request(request)
        if not business:
            return False
        if hasattr(obj, "business"):
            return obj.business_id == business.id
        return False


class IsOwnerOnly(permissions.BasePermission):
    """Only OWNER can perform (e.g. delete business, manage staff)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.OWNER
