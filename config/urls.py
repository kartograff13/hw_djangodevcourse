from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from config import settings
from courses.views import CourseViewSet
from users.views import PaymentViewSet

router = routers.DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("courses.urls")),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
