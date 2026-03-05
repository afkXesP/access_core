import jwt
import uuid
from django.conf import settings
from datetime import datetime

def generate_jwt(user):
    """
    Генерирует JWT access token для пользователя.

    Payload содержит:
        user_id — идентификатор пользователя
        role — роль пользователя
        jti — уникальный id токена
        iat — время создания
        exp — время истечения
    """
    payload = {
        "user_id": user.id,
        'role': user.role.name if user.role else None,
        'jti': str(uuid.uuid4()),
        "iat": datetime.now(),
        "exp": datetime.now() + settings.JWT_ACCESS_TOKEN_LIFETIME,
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return token