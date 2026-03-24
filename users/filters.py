import django_filters

from users.models import Payment


class PaymentFilter(django_filters.FilterSet):
    """Фильтр для модели Payment (фильтрация по курсу, уроку, методу оплаты"""

    course = django_filters.NumberFilter(field_name="course__id")
    lesson = django_filters.NumberFilter(field_name="lesson__id")
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)

    class Meta:
        model = Payment
        fields = ["course", "lesson", "payment_method"]
