from django.urls import include, path
from rest_framework import routers

from courses.views import CourseViewSet, LessonViewSet

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"lessons", LessonViewSet, basename="lessons")

urlpatterns = [
    path("", include(router.urls)),
]
