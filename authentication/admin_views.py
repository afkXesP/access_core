from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied

from .models import Role, BusinessElement, AccessRoleRule, User
from .admin_serializers import RoleSerializer, BusinessElementSerializer, AccessRoleRuleSerializer, \
    UserRoleUpdateSerializer


class AdminOnlyMixin:
    """
    Ограничивает доступ к endpoint только администраторам.
    Проверяет роль пользователя перед выполнением запроса
    """
    def initial(self, request, *args, **kwargs):
        if not request.user or not request.user.role:
            raise PermissionDenied("Authentication required")

        if request.user.role and request.user.role.name != 'admin':
            raise PermissionDenied("Only admins can access")

        super().initial(request, *args, **kwargs)


class RoleViewSet(AdminOnlyMixin, ModelViewSet):
    """
    API управления ролями пользователей.
    Доступно только администраторам.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class BusinessElementViewSet(AdminOnlyMixin, ModelViewSet):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer


class UserViewSet(AdminOnlyMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        request = self.request

        if instance == request.user:
            raise PermissionDenied("You can't update your own role")

        serializer.save()

    def perform_destroy(self, instance):
        if instance.role.name  == 'admin':
            admins_count = User.objects.filter(role__name='admin').count()
            if admins_count <= 1:
                raise PermissionDenied("You can't delete the last admin")

            instance.delete()


class AccessRoleRuleViewSet(AdminOnlyMixin, ModelViewSet):
    """
    API управления правилами RBAC.
    Позволяет администраторам настраивать
    права доступа ролей к бизнес-ресурсам.
    """
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
