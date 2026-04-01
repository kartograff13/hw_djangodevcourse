from rest_framework import serializers

from courses.models import Course, Lesson
from courses.validators import validate_youtube_url


class LessonsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""

    video_url = serializers.URLField(
        validators=[validate_youtube_url], required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    (Добавляет вычисляемое поле lessons_count, которое возвращает количество
    уроков, связанных с курсом)
    """

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonsSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        """Возвращает количество уроков для данного курса"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Возвращает статус подписки пользователя на объект"""
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False
