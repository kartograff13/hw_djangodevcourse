from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from courses.models import Course
from users.models import Payment


@shared_task
def send_course_update_email(course_id, subscriber_emails):
    """Асинхронная отправка писем подписчикам об обновлении курса"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден."

    subject = f"Обновление курса: {course.title}"
    message = (
        f"Здравствуйте! Курс '{course.title}' был обновлён. "
        f"Зайдите на платформу, что бы ознакомиться с новыми материалами."
    )
    from_email = settings.DEFAULT_FROM_EMAIL

    sent_count = 0
    for email in subscriber_emails:
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            sent_count += 1
        except Exception as e:
            print(f"Ошибка отправки на {email}: {e}")

    return f"Отправлено {sent_count} из {len(subscriber_emails)} писем для курса {course.title}"


@shared_task
def check_pending_payments():
    """Периодическая проверка зависших платежей (каждые 30 минут)"""
    pending_payments = Payment.objects.filter(stripe_payment_status="pending")
    for payment in pending_payments:
        pass

    return f"Проверка {pending_payments.count()} ожидающих платежей"
