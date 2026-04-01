from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.filters import PaymentFilter
from users.models import Payment, User
from users.serializers import PaymentSerializer, PublicUserSerializer, UserRegistrationSerializer, UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""

    queryset = Payment.objects.all().select_related("user", "course", "lesson")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
    permission_classes = [permissions.IsAuthenticated]


class UserProfileView(RetrieveUpdateAPIView):
    """Получение и обновление профиля текущего пользователя"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRegistrationView(generics.CreateAPIView):
    """Представление для регистрации нового пользователя"""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Обработка POST-запроса на регистрацию"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями (CRUD)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class PublicUserDetailView(generics.RetrieveAPIView):
    """Просмотр профиля любого пользователя (только чтение, публичные поля)"""

    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.IsAuthenticated]
