import stripe
from django.urls import reverse

from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_session(course, user):
    """Создаёт продукт, цену и сессию оплаты в Stripe"""

    product = stripe.Product.create(
        name=course.title,
        description=course.description,
    )
    stripe_product_id = product.id

    price = stripe.Price.create(
        product=stripe_product_id,
        unit_amount=int(course.amount * 100),
        currency="rub",
    )
    stripe_price_id = price.id

    success_url = settings.SITE_URL + reverse("payment-success")
    cancel_url = settings.SITE_URL + reverse("payment-cancel")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "course_id": course.id,
            "user_id": user.id,
        },
    )

    return {
        "product_id": stripe_product_id,
        "price_id": stripe_price_id,
        "session_id": session.id,
        "session_url": session.url,
    }
