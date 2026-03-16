from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Role(models.Model):
    """
    Роль пользователя в системе.

    Используется в RBAC модели для определения прав доступа.
    Примеры ролей: admin, user, manager.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """
    Менеджер пользователей
    """
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.

    Используется email вместо username.
    Поддерживает soft delete через поле is_active.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email


class BusinessElement(models.Model):
    """
    Объекты бизнес-приложения, которым регулируется доступ
    """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """
    Правило доступа роли к определенному элементу системы.

    Реализует RBAC модель:
    Role -> AccessRoleRule -> BusinessElement

    permission поля определяют какие действия может выполнять
    пользователь с объектами системы.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)

    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)

    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"


class BlacklistedToken(models.Model):
    """
    Таблица blacklist JWT токенов.

    Используется для реализации logout:
    после выхода пользователя jti токена сохраняется в blacklist
    и дальнейшее использование этого токена запрещается.
    """
    jti = models.UUIDField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.jti)
