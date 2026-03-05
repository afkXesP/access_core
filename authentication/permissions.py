from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import APIException

from rbac.services import check_access


class RBACPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        element_name = getattr(view, "business_element", None)

        if not element_name:
            raise APIException("RBAC permission requires business_element")

        if not check_access(request.user, element_name, request.method):
            raise PermissionDenied("Access denied")

        return True