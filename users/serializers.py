from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа"""

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для платежей в профиле пользователя (без поля user)"""

    course = serializers.StringRelatedField(read_only=True)
    lesson = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "payment_date", "course", "lesson", "amount", "payment_method")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя с историей платежей"""

    payments = PaymentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar", "payments")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "city", "avatar", "password", "password2")

    def validate(self, attrs):
        """Проверяет совпадение пароля и подтверждение"""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Поля паролей не совпадают."})
        return attrs

    def create(self, validated_data):
        """Создаёт пользователя (удаляя поле 'password2')"""
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра любого профиля (без фамилии и платежей)"""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "phone", "city", "avatar")
