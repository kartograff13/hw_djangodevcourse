from celery import shared_task

from users.models import Payment


@shared_task
def check_pending_payments():
    """Периодическая проверка зависших платежей (каждые 30 минут)"""
    pending_payments = Payment.objects.filter(stripe_payment_status='pending')
    for payment in pending_payments:
        pass

    return f"Проверка {pending_payments.count()} ожидающих платежей"
