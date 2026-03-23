from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    username = None
    email = models.EmailField(
        unique=True, verbose_name="Электронная почта", help_text="Укажите Вашу электронную почту"
    )
    phone = PhoneNumberField(
        blank=True, null=True, verbose_name="Телефон", help_text="Укажите Ваш номер телефона"
    )
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Город", help_text="Укажите Ваш город")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар", help_text="Загрузите свой аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
