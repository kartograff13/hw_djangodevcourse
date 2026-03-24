from rest_framework import serializers

from users.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа"""

    class Meta:
        model = Payment
        fields = "__all__"
