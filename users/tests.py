from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from courses.models import Course
from users.models import Payment

User = get_user_model()


class RegistrationTests(APITestCase):
    """Набор тестов для регистрации пользователя"""

    def test_register_success(self):
        """Тест успешной регистрации: возвращает токены и данные пользователя"""
        url = reverse("user-register")
        data = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "newuser@example.com")

    def test_register_password_mismatch(self):
        """Тест ошибки при несовпадении пароля и подтверждения"""
        url = reverse("user-register")
        data = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password2": "different",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class TokenTests(APITestCase):
    """Набор тестов для JWT аутентификации"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

    def test_token_obtain(self):
        """Проверка успешного получения токенов при правильных учётных данных"""
        url = reverse("token_obtain_pair")
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        """Проверка возможности обновления access токена через refresh"""
        # Получить токен
        obtain_url = reverse("token_obtain_pair")
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(obtain_url, data)
        refresh = response.data["refresh"]

        # Обновить
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh}
        response = self.client.post(refresh_url, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_obtain_invalid(self):
        """Проверка возврата 401 при неверных учётных данных"""
        url = reverse("token_obtain_pair")
        data = {"email": "test@example.com", "password": "wrong"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(APITestCase):
    """Набор тестов для работы с профилем пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass123", first_name="John", last_name="Doe"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="testpass123", first_name="Jane", last_name="Smith"
        )
        self.course = Course.objects.create(title="Course", owner=self.user)
        Payment.objects.create(user=self.user, course=self.course, amount=100.00, payment_method="cash")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_own_profile_retrieve(self):
        """Тест получения собственного профиля: должны быть все поля и платежи"""
        url = reverse("user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["last_name"], "Doe")
        self.assertIn("payments", response.data)
        self.assertEqual(len(response.data["payments"]), 1)

    def test_own_profile_update(self):
        """Тест обновления собственного профиля (PATCH)"""
        url = reverse("user-profile")
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_public_profile_retrieve(self):
        """Тест публичного профиля: возвращает ограниченный набор полей (без фамилии и платежей)"""
        url = reverse("user-user-detail", args=[self.other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "other@example.com")
        self.assertEqual(response.data["first_name"], "Jane")
        self.assertNotIn("last_name", response.data)  # фамилия скрыта
        self.assertNotIn("payments", response.data)

    def test_public_profile_unauthenticated(self):
        """Тест доступа к публичному профилю без аутентификации: требуется авторизация"""
        client = APIClient()
        url = reverse("user-user-detail", args=[self.other_user.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_other_profile_not_allowed(self):
        """Тест запрета на редактирование чужого профиля (доступно только админам)"""
        url = reverse("users-detail", args=[self.other_user.id])
        response = self.client.patch(url, {"first_name": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserAdminTests(APITestCase):
    """Набор тестов для административного интерфейса управления пользователями"""

    def setUp(self):
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_list_users(self):
        """Администратор может получить список всех пользователей"""
        url = reverse("users-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 2)

    def test_admin_can_update_user(self):
        """Администратор может редактировать данные любого пользователя"""
        url = reverse("users-detail", args=[self.user.id])
        data = {"first_name": "NewName"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewName")

    def test_non_admin_cannot_access_user_list(self):
        """Обычный пользователь не может получить список всех пользователей"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("users-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentTests(APITestCase):
    """Набор тестов для CRUD операций с платежами"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.course = Course.objects.create(title="Course", owner=self.user)
        self.payment = Payment.objects.create(user=self.user, course=self.course, amount=100.00, payment_method="cash")
        self.client = APIClient()

    def test_payment_list_authenticated(self):
        """Аутентифицированный пользователь может просматривать список платежей"""
        self.client.force_authenticate(user=self.user)
        url = reverse("payments-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_payment_filter_by_course(self):
        """Фильтрация платежей по курсу"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments-list") + f"?course={self.course.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["course"], self.course.id)

    def test_payment_filter_by_payment_method(self):
        """Фильтрация платежей по способу оплаты"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments-list") + "?payment_method=cash"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_payment_create(self):
        """Создание нового платежа (доступно администратору)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments-list")
        data = {"user": self.user.id, "course": self.course.id, "amount": 200.00, "payment_method": "transfer"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_payment_update(self):
        """Обновление существующего платежа (доступно администратору)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments-detail", args=[self.payment.id])
        data = {"amount": 150.00}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.amount, 150.00)

    def test_payment_delete(self):
        """Удаление платежа (доступно администратору)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments-detail", args=[self.payment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Payment.objects.filter(id=self.payment.id).exists())

    def test_unauthenticated_cannot_access_payments(self):
        """Не аутентифицированный пользователь не может получить список платежей"""
        url = reverse("payments-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
