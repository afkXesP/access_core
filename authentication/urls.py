from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .admin_views import RoleViewSet, BusinessElementViewSet, AccessRoleRuleViewSet, UserViewSet

router = DefaultRouter()
router.register('admin/roles', RoleViewSet)
router.register('admin/elements', BusinessElementViewSet)
router.register('admin/rules', AccessRoleRuleViewSet)
router.register('admin/users', UserViewSet)


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users/me/', views.UserView.as_view(), name='user-me'),
]

urlpatterns += router.urls
