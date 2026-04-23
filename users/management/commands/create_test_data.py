from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone

from courses.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    """Создаёт тестовые данные для платежей"""

    def handle(self, *args, **options):
        user1, created1 = User.objects.get_or_create(
            email="student@example.com",
            defaults={"first_name": "Иван", "last_name": "Петров", "phone": "+79999999999", "city": "Москва"},
        )
        if created1:
            user1.set_password("testpass123")
            user1.save()
            self.stdout.write(self.style.SUCCESS(f"Создан пользователь {user1.email}"))

        user2, created2 = User.objects.get_or_create(
            email="teacher@example.com",
            defaults={
                "first_name": "Анна",
                "last_name": "Сидорова",
                "phone": "+788888888888",
                "city": "Санкт-Петербург",
            },
        )
        if created2:
            user2.set_password("testpass123")
            user2.save()
            self.stdout.write(self.style.SUCCESS(f"Создан пользователь {user2.email}"))

        course1, _ = Course.objects.get_or_create(
            title="Django для начинающих", defaults={"description": "Полный курс Django с нуля"}
        )
        self.stdout.write(f"Курс {course1.title} создан.")

        course2, _ = Course.objects.get_or_create(
            title="REST API на Django", defaults={"description": "Создание API с помощью DRF"}
        )
        self.stdout.write(f"Курс {course2.title} создан.")

        lesson1, _ = Lesson.objects.get_or_create(
            title="Введение в Django",
            course=course1,
            defaults={
                "description": "Что такое Django и установка",
                "video_url": "https://example.com/course1/lessons/1/video1",
            },
        )

        lesson2, _ = Lesson.objects.get_or_create(
            title="Модели и миграции",
            course=course1,
            defaults={
                "description": "Работа с базами данных (БД)",
                "video_url": "https://example.com/course1/lessons/2/video2",
            },
        )

        lesson3, _ = Lesson.objects.get_or_create(
            title="Сериализаторы DRF",
            course=course2,
            defaults={
                "description": "Создание сериализаторов",
                "video_url": "https://example.com/course2/lessons/3/video3",
            },
        )
        self.stdout.write("Уроки созданы.")

        Payment.objects.get_or_create(
            user=user1,
            course=course1,
            defaults={
                "amount": 5000.00,
                "payment_method": "cash",
                "payment_date": timezone.now(),
            },
        )

        Payment.objects.get_or_create(
            user=user2,
            lesson=lesson3,
            defaults={
                "amount": 1500.00,
                "payment_method": "transfer",
                "payment_date": timezone.now(),
            },
        )

        Payment.objects.get_or_create(
            user=user1,
            course=course2,
            defaults={
                "amount": 7500.00,
                "payment_method": "transfer",
                "payment_date": timezone.now(),
            },
        )
        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены."))
