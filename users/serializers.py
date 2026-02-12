from rest_framework import serializers
from .models import User, Payment

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели :model:`users.User`.
    Используется при регистрации и просмотре профиля.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Создаёт нового пользователя с зашифрованным паролем.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели :model:`users.Payment`.
    """
    class Meta:
        model = Payment
        fields = '__all__'