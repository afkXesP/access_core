import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from authentication.models import User, Role, BlacklistedToken


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_role(db):
    role, _ = Role.objects.get_or_create(name="user")
    return role


@pytest.fixture
def admin_role(db):
    role, _ = Role.objects.get_or_create(name="admin")
    return role


@pytest.fixture
def user(db, user_role):
    user =  User.objects.create(email='user@test.com', name='User', role=user_role, is_active=True)
    user.set_password('password123')
    user.save()

    return user


@pytest.fixture
def login_token(client, user):
    response = client.post('/api/login/', {'email': 'user@test.com', 'password': 'password123'})
    return response.data['access_token']


@pytest.mark.django_db
def test_register_success(client):
    response = client.post('/api/register/', {'email': 'new@test.com', 'name': 'New user', 'password': 'password123',
                                             'password_repeat': 'password123'})

    assert response.status_code == 201
    assert 'access_token' in response.data


@pytest.mark.django_db
def test_register_password_mismatch(client):
    response = client.post('/api/register/', {'email': 'new@test.com', 'name': 'New user', 'password': 'password123',
                                              'password_repeat': '123'})

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email(client, user):
    response = client.post("/api/register/", {"email": "user@test.com", "name": "New user", "password": "password123",
                                              "password_repeat": "password123" })

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_success(client, user):
    response = client.post("/api/login/", {"email": "user@test.com", "password": "password123"})

    assert response.status_code == 200
    assert "access_token" in response.data


@pytest.mark.django_db
def test_login_wrong_password(client, user):
    response = client.post("/api/login/", { "email": "user@test.com", "password": "wrongpass"})

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_user_not_active(client, user):
    user.is_active = False
    user.save()

    response = client.post("/api/login/", {"email": "user@test.com", "password": "password123"
    })

    assert response.status_code == 403


@pytest.mark.django_db
def test_logout(client, login_token):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_token}")

    response = client.post("/api/logout/")

    assert response.status_code == 200
    assert BlacklistedToken.objects.count() == 1
