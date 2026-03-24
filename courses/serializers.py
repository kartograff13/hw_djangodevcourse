from rest_framework import serializers

from courses.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    (Добавляет вычисляемое поле lessons_count, которое возвращает количество
    уроков, связанных с курсом)
    """

    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        """Возвращает количество уроков для данного курса"""
        return obj.lessons.count()


class LessonsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""

    class Meta:
        model = Lesson
        fields = "__all__"
