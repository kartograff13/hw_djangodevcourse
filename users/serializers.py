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
