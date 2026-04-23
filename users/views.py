import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from courses.models import Course
from users.filters import PaymentFilter
from users.models import Payment, User
from users.serializers import PaymentSerializer, PublicUserSerializer, UserRegistrationSerializer, UserSerializer
from users.stripe_service import create_stripe_payment_session


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


class CreatePaymentView(APIView):
    """Представление для создания платежа через Stripe"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"error": "Course ID required"}, status=400)
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)
        amount = course.price

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            payment_method="transfer",
            stripe_payment_status="pending",
        )

        stripe_data = create_stripe_payment_session(course, request.user, amount)

        payment.stripe_product_id = stripe_data["product_id"]
        payment.stripe_price_id = stripe_data["price_id"]
        payment.stripe_session_id = stripe_data["session_id"]
        payment.payment_url = stripe_data["session_url"]
        payment.save()

        return Response(
            {
                "payment_id": payment.id,
                "payment_url": stripe_data["session_url"],
            },
            status=201,
        )


class CheckPaymentStatusView(APIView):
    """Представление для проверки статуса платежа через Stripe"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)

        if session.payment_status == "paid" and payment.stripe_payment_status != "paid":
            payment.stripe_payment_status = "paid"
            payment.save()

        return Response({"status": payment.stripe_payment_status})


class PaymentSuccessView(APIView):
    """Представление для обработки успешной оплаты"""

    def get(self, request):
        return Response({"message": "Payment successful"}, status=200)


class PaymentCancelView(APIView):
    """Представление для обработки отмены оплаты"""

    def get(self, request):
        return Response({"message": "Payment canceled"}, status=200)
