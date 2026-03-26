from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config import settings
from users.views import PaymentViewSet, UserProfileView, UserRegistrationView, UserViewSet

router = routers.DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("courses.urls")),
    path("api/", include(router.urls)),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/register/", UserRegistrationView.as_view(), name="user-register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
