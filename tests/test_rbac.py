import pytest
from rest_framework.test import APIClient

from authentication.models import User, Role, BusinessElement, AccessRoleRule


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_role(db):
    role, _ = Role.objects.get_or_create(name="admin")
    return role


@pytest.fixture
def user_role(db):
    role, _ = Role.objects.get_or_create(name="user")
    return role


@pytest.fixture
def business_elements(db):
    orders, _ = BusinessElement.objects.get_or_create(name="orders")
    products, _ = BusinessElement.objects.get_or_create(name="products")
    reports, _ = BusinessElement.objects.get_or_create(name="reports")

    return {"orders": orders, "products": products, "reports": reports,}


@pytest.fixture
def access_rules(db, admin_role, user_role, business_elements):
    AccessRoleRule.objects.get_or_create(role=admin_role, element=business_elements["orders"], read_permission=True,
                                  create_permission=True,)

    AccessRoleRule.objects.get_or_create(role=admin_role, element=business_elements["reports"], read_permission=True,)

    AccessRoleRule.objects.get_or_create(role=user_role, element=business_elements["orders"], read_permission=True,)


@pytest.fixture
def admin_user(db, admin_role):
    user = User.objects.create(email="admin@test.com", name="Admin", role=admin_role, is_active=True,)
    user.set_password("password123")
    user.save()
    return user


@pytest.fixture
def normal_user(db, user_role):
    user = User.objects.create(email="user@test.com", name="User", role=user_role, is_active=True,)
    user.set_password("password123")
    user.save()
    return user


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post( "/api/login/", {"email": "admin@test.com", "password": "password123"},)
    return response.data["access_token"]


@pytest.fixture
def user_token(client, normal_user):
    response = client.post("/api/login/", {"email": "user@test.com", "password": "password123"},)
    return response.data["access_token"]


@pytest.mark.django_db
def test_user_can_read_orders(client, user_token, access_rules):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")
    response = client.get("/api/orders/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_cannot_create_orders(client, user_token, access_rules):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")
    response = client.post("/api/orders/", {"title": "test"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_access_reports(client, user_token, access_rules):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")
    response = client.get("/api/reports/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_access_reports(client, admin_token, access_rules):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    response = client.get("/api/reports/")
    assert response.status_code == 200


def test_unauthorized_access(client):
    response = client.get("/api/orders/")
    assert response.status_code == 403
