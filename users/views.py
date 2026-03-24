from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateAPIView

from users.filters import PaymentFilter
from users.models import Payment
from users.serializers import PaymentSerializer, UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""

    queryset = Payment.objects.all().select_related("user", "course", "lesson")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


class UserProfileView(RetrieveUpdateAPIView):
    """Получение и обновление профиля текущего пользователя"""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
