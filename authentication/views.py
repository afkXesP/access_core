import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User, BlacklistedToken
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .utils.utils_jwt import generate_jwt


class RegisterView(APIView):
    """
    Регистрация нового пользователя.
    Создает пользователя и сразу выдает JWT токен
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token = generate_jwt(user)
        return Response({'message': 'User registered successfully', "access_token": token, "token_type": "Bearer"},
                        status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Аутентификация пользователя по email и паролю.
    При успешной проверке возвращает JWT access token
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'Account is deactivated'}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_jwt(user)
        return Response({'access_token': token, 'token_type': 'Bearer'})


class LogoutView(APIView):
    """
    Logout пользователя.
    JWT токен добавляется в blacklist, после чего его использование становится невозможным
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Expired token'}, status=status.HTTP_401_UNAUTHORIZED)

        jti = payload['jti']
        BlacklistedToken.objects.create(jti=jti)

        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class UserView(APIView):
    """
    Управление профилем пользователя.

    GET - получить данные профиля
    PATCH - обновить данные
    DELETE - мягкое удаление аккаунта
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        jti = payload.get('jti')
        BlacklistedToken.objects.create(jti=jti)

        return Response(status=status.HTTP_204_NO_CONTENT)
