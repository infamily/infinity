from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActive(BasePermission):
    """
    Allows access only to authenticated and `is_active` users.
    """

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                and request.user.is_active)
