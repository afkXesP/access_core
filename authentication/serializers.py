from rest_framework import serializers

from .models import User, Role


class RegisterSerializer(serializers.Serializer):
    """
    Сериализатор регистрации пользователя
    """
    email = serializers.EmailField()
    name = serializers.CharField(max_length=200)

    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)


    def validate(self, attrs):
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError("Passwords must match")

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("Email already registered")

        return attrs

    def create(self, validated_data):
        # Если пользователей нет, тогда первый пользователь - админ
        if User.objects.exists():
            role, _ = Role.objects.get_or_create(name='user')
        else:
            role, _ = Role.objects.get_or_create(name='admin')

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            role=role,
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор авторизации  пользователя
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя
    """
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'password']
        read_only_fields = ['id', 'email', 'role']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.name = validated_data.get('name', instance.name)

        if password:
            instance.set_password(password)

        instance.save()
        return instance