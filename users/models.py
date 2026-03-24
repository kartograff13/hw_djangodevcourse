from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from courses.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    """Менеджер для модели User с авторизацией по email"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email должен быть указан.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    username = None
    email = models.EmailField(
        unique=True, verbose_name="Электронная почта", help_text="Укажите Вашу электронную почту"
    )
    phone = PhoneNumberField(blank=True, null=True, verbose_name="Телефон", help_text="Укажите Ваш номер телефона")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Город", help_text="Укажите Ваш город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите свой аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа пользователя за курс или урок"""

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments", verbose_name="Пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=10, verbose_name="Способ оплаты")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(course__isnull=False, lesson__isnull=True)
                    | models.Q(course__isnull=True, lesson__isnull=False)
                ),
                name="only_one_product_paid",
            )
        ]

    def __str__(self):
        product = self.course if self.course else self.lesson
        return f"{self.user.email} - {product} - {self.amount} ({self.get_payment_method_display()})"
