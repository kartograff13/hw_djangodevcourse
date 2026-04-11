from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Subscription
from courses.paginators import StandardResultsSetPagination
from courses.serializers import CourseSerializer, LessonsSerializer
from users.permissions import IsModeratorOrOwner
from users.tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для полного CRUD курсов"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Возвращает список курсов в зависимости от прав пользователя"""
        user = self.request.user

        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Сохраняет новый курс автоматически сохраняя владельца"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Выполняет обновление курса и отправляет уведомление подписчикам с ограничением частоты"""
        course = serializer.save()
        last_sent = course.last_notification_sent
        if not last_sent or (timezone.now() - last_sent) > timedelta(hours=4):
            subscriber_emails = course.subscriptions.values_list("user__email", flat=True)
            if subscriber_emails:
                send_course_update_email.delay(course.id, list(subscriber_emails))
            course.last_notification_sent = timezone.now()
            course.save(update_fields=["last_notification_sent"])


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet для полного CRUD уроков"""

    serializer_class = LessonsSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Возвращает список уроков в зависимости от прав пользователя"""
        user = self.request.user

        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Сохраняет новый урок автоматически сохраняя владельца"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Выполняет обновление урока и отправляет уведомление подписчикам курса с ограничением по частоте (4 часа)"""
        lesson = serializer.save()
        course = lesson.course
        if course:
            last_sent = course.last_notification_sent
            if not last_sent or (timezone.now() - last_sent) > timedelta(hours=4):
                subscriber_emails = course.subscriptions.values_list("user__email", flat=True)
                if subscriber_emails:
                    send_course_update_email.delay(course.id, list(subscriber_emails))
                course.last_notification_sent = timezone.now()
                course.save(update_fields=["last_notification_sent"])


class SubscriptionView(APIView):
    """Представление для управления подписками пользователя на курсы"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Обрабатывает POST-запрос на подписку/отписку от курса"""
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "course does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscription.objects.filter(user=request.user, course=course)

        if subscription.exists():
            subscription.delete()
            return Response({"status": "unsubscribed"}, status=status.HTTP_200_OK)
        else:
            Subscription.objects.create(user=request.user, course=course)
            return Response({"status": "subscribed"}, status=status.HTTP_201_CREATED)
