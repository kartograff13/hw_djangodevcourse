from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from courses.models import Course, Lesson
from courses.serializers import CourseSerializer, LessonsSerializer
from users.permissions import IsModeratorOrOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для полного CRUD курсов"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        """Возвращает список курсов в зависимости от прав пользователя"""
        user = self.request.user

        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Сохраняет новый курс автоматически сохраняя владельца"""
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet для полного CRUD уроков"""

    serializer_class = LessonsSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        """Возвращает список уроков в зависимости от прав пользователя"""
        user = self.request.user

        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Сохраняет новый урок автоматически сохраняя владельца"""
        serializer.save(owner=self.request.user)
