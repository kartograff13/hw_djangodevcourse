from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from config import settings
from users.views import PaymentViewSet, UserProfileView

router = routers.DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("courses.urls")),
    path("api/", include(router.urls)),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
