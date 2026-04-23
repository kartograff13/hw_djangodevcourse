from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config import settings
from users.views import (
    CheckPaymentStatusView,
    CreatePaymentView,
    PaymentCancelView,
    PaymentSuccessView,
    PaymentViewSet,
    PublicUserDetailView,
    UserProfileView,
    UserRegistrationView,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("courses.urls")),
    path("api/", include(router.urls)),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/profiles/<int:pk>/", PublicUserDetailView.as_view(), name="user-user-detail"),
    path("api/register/", UserRegistrationView.as_view(), name="user-register"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/payments/create/", CreatePaymentView.as_view(), name="payment-create"),
    path("api/payments/status/<int:payment_id>/", CheckPaymentStatusView.as_view(), name="payment-status"),
    path("stripe/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("stripe/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
