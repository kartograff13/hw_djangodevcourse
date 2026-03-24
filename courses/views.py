from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from courses.models import Course, Lesson
from courses.serializers import CourseSerializer, LessonsSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для полного CRUD курсов"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListCreateView(ListCreateAPIView):
    """Получение списка уроков и создание нового"""

    queryset = Lesson.objects.all()
    serializer_class = LessonsSerializer


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление одного урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonsSerializer
