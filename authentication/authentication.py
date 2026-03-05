import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User, BlacklistedToken


class JWTAuthentication(BaseAuthentication):
    """
    Кастомная JWT аутентификация.

    Извлекает токен из заголовка:
        Authorization: Bearer <token>

    Проверяет:
        - валидность токена
        - срок действия
        - наличие в blacklist

    Если проверка успешна - устанавливает request.user.
    """
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid token header")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM,)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")

        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        jti = payload.get("jti")

        if BlacklistedToken.objects.filter(jti=jti).exists():
            raise AuthenticationFailed("Token blacklisted")

        user_id = payload.get("user_id")

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, token)