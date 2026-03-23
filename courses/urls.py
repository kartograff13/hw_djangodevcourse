from django.urls import include, path
from rest_framework import routers

from courses.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", LessonListCreateView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDestroyView.as_view(), name="lesson-detail"),
]
