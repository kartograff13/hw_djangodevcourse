from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from courses.models import Course
from users.models import Payment, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "first_name", "last_name", "phone", "city", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "phone", "city", "avatar")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "first_name", "last_name", "phone", "city", "avatar"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_date", "course", "lesson", "amount", "payment_method")
    list_filter = ("payment_method", "payment_date")
    search_fields = ("user__email", "course__title", "lesson__title")
