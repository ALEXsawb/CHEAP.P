from rest_framework import permissions
from .serializers import for_staff


def check_is_staff(view):
    if 'ForStaff' not in view.serializer_class.__name__:
        staff_serializer_name = view.serializer_class.__name__ + 'ForStaff'
        if staff_serializer_name in for_staff.__dict__:
            view.serializer_class = for_staff.__getattribute__(staff_serializer_name)
    return True


class AdminOrRead(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Достали второй return с класса IsAdminUser """
        if bool(request.user and request.user.is_staff):
            return check_is_staff(view)

        if request.method in permissions.SAFE_METHODS:
            return True
        return False
