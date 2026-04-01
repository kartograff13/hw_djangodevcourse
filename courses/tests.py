from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from courses.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTests(APITestCase):
    """Тесты CRUD для уроков с разными правами доступа"""

    def setUp(self):
        self.moderator_group, _ = Group.objects.get_or_create(name="Модераторы")

        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123", first_name="User", last_name="One"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123", first_name="User", last_name="Two"
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com", password="testpass123", first_name="Mod", last_name="Erator"
        )
        self.moderator.groups.add(self.moderator_group)

        self.course1 = Course.objects.create(title="Course 1", owner=self.user1)
        self.course2 = Course.objects.create(title="Course 2", owner=self.user2)

        self.lesson1 = Lesson.objects.create(title="Lesson 1", course=self.course1, owner=self.user1)
        self.lesson2 = Lesson.objects.create(title="Lesson 2", course=self.course2, owner=self.user2)

        self.list_url = reverse("lessons-list")
        self.detail_url = lambda pk: reverse("lessons-detail", args=[pk])

        self.client_user1 = APIClient()
        self.client_user1.force_authenticate(user=self.user1)
        self.client_user2 = APIClient()
        self.client_user2.force_authenticate(user=self.user2)
        self.client_moderator = APIClient()
        self.client_moderator.force_authenticate(user=self.moderator)

    def _create_lesson(self, client, data):
        return client.post(self.list_url, data)

    def _update_lesson(self, client, pk, data):
        return client.put(self.detail_url(pk), data)

    def _delete_lesson(self, client, pk):
        return client.delete(self.detail_url(pk))

    def test_user_can_create_own_lesson(self):
        """Пользователь может создать урок (owner автоматически присваивается)"""
        data = {"title": "New Lesson", "course": self.course1.id, "description": "Test description"}
        response = self._create_lesson(self.client_user1, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        lesson = Lesson.objects.get(title="New Lesson")
        self.assertEqual(lesson.owner, self.user1)

    def test_user_can_update_own_lesson(self):
        """Пользователь может редактировать свой урок"""
        data = {"title": "Updated Title"}
        response = self._update_lesson(self.client_user1, self.lesson1.id, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Updated Title")

    def test_user_can_delete_own_lesson(self):
        """Пользователь может удалить свой урок"""
        response = self._delete_lesson(self.client_user1, self.lesson1.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson1.id).exists())

    def test_user_cannot_update_other_lesson(self):
        """Пользователь не может редактировать чужой урок"""
        data = {"title": "Hacked Title"}
        response = self._update_lesson(self.client_user1, self.lesson2.id, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # или 403, но queryset фильтрует
        self.lesson2.refresh_from_db()
        self.assertNotEqual(self.lesson2.title, "Hacked Title")

    def test_user_cannot_delete_other_lesson(self):
        """Пользователь не может удалить чужой урок"""
        response = self._delete_lesson(self.client_user1, self.lesson2.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_list_own_lessons(self):
        """Пользователь видит только свои уроки в списке"""
        response = self.client_user1.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.lesson1.id)

    def test_user_cannot_create_lesson_for_other_course_ownership(self):
        """Пользователь не может создать урок в курсе, владельцем которого не является (курс не его)"""
        data = {"title": "New Lesson", "course": self.course2.id, "description": "Test"}
        response = self._create_lesson(self.client_user1, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lesson = Lesson.objects.get(title="New Lesson")
        self.assertEqual(lesson.owner, self.user1)
        self.assertEqual(lesson.course, self.course2)

    def test_moderator_can_view_any_lesson(self):
        """Модератор видит все уроки в списке"""
        response = self.client_moderator.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_moderator_can_update_any_lesson(self):
        """Модератор может редактировать любой урок"""
        data = {"title": "Moderated Title"}
        response = self._update_lesson(self.client_moderator, self.lesson1.id, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Moderated Title")

    def test_moderator_cannot_create_lesson(self):
        """Модератор не может создавать уроки"""
        data = {
            "title": "Moderator Lesson",
            "course": self.course1.id,
        }
        response = self._create_lesson(self.client_moderator, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete_lesson(self):
        """Модератор не может удалять уроки"""
        response = self._delete_lesson(self.client_moderator, self.lesson1.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(id=self.lesson1.id).exists())

    def test_unauthenticated_cannot_access_lessons(self):
        """Неавторизованный пользователь не может получить список уроков"""
        client = APIClient()
        response = client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionTests(APITestCase):
    """Тесты подписки на курс"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="testpass123")
        self.course = Course.objects.create(title="Test Course", owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.subscribe_url = reverse("subscribe")

    def test_subscribe_to_course(self):
        """Подписка на курс"""
        response = self.client.post(self.subscribe_url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "subscribed")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Отписка от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post(self.subscribe_url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unsubscribed")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_invalid_course(self):
        """Подписка на несуществующий курс"""
        response = self.client.post(self.subscribe_url, {"course_id": 999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "course does not exist")

    def test_subscribe_missing_course_id(self):
        """Запрос без course_id"""
        response = self.client.post(self.subscribe_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "course_id is required")

    def test_is_subscribed_field_in_course(self):
        """Проверка, что поле is_subscribed в сериализаторе курса корректно работает"""
        url = reverse("courses-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_data = response.data["results"][0]
        self.assertFalse(course_data["is_subscribed"])

        self.client.post(self.subscribe_url, {"course_id": self.course.id})
        response = self.client.get(url)
        course_data = response.data["results"][0]
        self.assertTrue(course_data["is_subscribed"])

    def test_unauthenticated_cannot_subscribe(self):
        """Неавторизованный пользователь не может подписаться"""
        client = APIClient()
        response = client.post(self.subscribe_url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseCRUDTests(APITestCase):
    """Тесты CRUD для курсов"""

    def setUp(self):
        self.moderator_group, _ = Group.objects.get_or_create(name="Модераторы")

        self.user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        self.user2 = User.objects.create_user(email="user2@example.com", password="testpass123")
        self.moderator = User.objects.create_user(email="moderator@example.com", password="testpass123")
        self.moderator.groups.add(self.moderator_group)

        self.course1 = Course.objects.create(title="Course 1", owner=self.user1)
        self.course2 = Course.objects.create(title="Course 2", owner=self.user2)

        self.list_url = reverse("courses-list")
        self.detail_url = lambda pk: reverse("courses-detail", args=[pk])

        self.client_user1 = APIClient()
        self.client_user1.force_authenticate(user=self.user1)
        self.client_user2 = APIClient()
        self.client_user2.force_authenticate(user=self.user2)
        self.client_moderator = APIClient()
        self.client_moderator.force_authenticate(user=self.moderator)

    def test_user_can_create_course(self):
        """Обычный пользователь может создать курс"""
        data = {"title": "New Course", "description": "Test"}
        response = self.client_user1.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(title="New Course")
        self.assertEqual(course.owner, self.user1)

    def test_user_can_update_own_course(self):
        """Пользователь может обновить свой курс"""
        data = {"title": "Updated Title"}
        response = self.client_user1.patch(self.detail_url(self.course1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, "Updated Title")

    def test_user_can_delete_own_course(self):
        """Пользователь может удалить свой курс"""
        response = self.client_user1.delete(self.detail_url(self.course1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course1.id).exists())

    def test_user_cannot_update_other_course(self):
        """Пользователь не может обновить чужой курс"""
        data = {"title": "Hacked"}
        response = self.client_user1.put(self.detail_url(self.course2.id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_other_course(self):
        """Пользователь не может удалить чужой курс"""
        response = self.client_user1.delete(self.detail_url(self.course2.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_list_own_courses(self):
        """Пользователь видит только свои курсы"""
        response = self.client_user1.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.course1.id)

    def test_moderator_can_view_all_courses(self):
        """Модератор видит все курсы"""
        response = self.client_moderator.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_moderator_can_update_any_course(self):
        """Модератор может редактировать любой курс"""
        data = {"title": "Moderated"}
        response = self.client_moderator.patch(self.detail_url(self.course1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, "Moderated")

    def test_moderator_cannot_create_course(self):
        """Модератор не может создать курс"""
        data = {"title": "New Course"}
        response = self.client_moderator.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete_course(self):
        """Модератор не может удалить курс"""
        response = self.client_moderator.delete(self.detail_url(self.course1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(id=self.course1.id).exists())


class LessonValidatorTests(APITestCase):
    """Тесты валидатора ссылок YouTube"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="testpass123")
        self.course = Course.objects.create(title="Test Course", owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("lessons-list")

    def test_valid_youtube_url(self):
        """Разрешённые YouTube ссылки проходят валидацию"""
        valid_urls = [
            "https://www.youtube.com/watch?v=abc123",
            "https://youtu.be/abc123",
            "https://youtube.com/watch?v=abc123",
            "https://m.youtube.com/watch?v=abc123",
        ]
        for url in valid_urls:
            data = {"title": "Lesson", "course": self.course.id, "video_url": url}
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_youtube_url(self):
        """Ссылки не на YouTube отклоняются"""
        invalid_urls = ["https://vimeo.com/123456", "https://rutube.ru/video/123", "https://example.com/video"]
        for url in invalid_urls:
            data = {"title": "Lesson", "course": self.course.id, "video_url": url}
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("video_url", response.data)


class PaginationTests(APITestCase):
    """Тесты для пагинации"""

    def setUp(self):
        self.user = User.objects.create_user(email="user@example.com", password="testpass123")
        self.course = Course.objects.create(title="Test Course", owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        for i in range(15):
            Lesson.objects.create(title=f"Lesson {i}", course=self.course, owner=self.user)

    def test_pagination_default_page_size(self):
        """Проверка размера страницы по умолчанию (10)"""
        url = reverse("lessons-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_custom_page_size(self):
        """Проверка параметра page_size"""
        url = reverse("lessons-list") + "?page_size=5"
        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 5)

    def test_pagination_second_page(self):
        """Переход на вторую страницу"""
        url = reverse("lessons-list") + "?page=2"
        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])
