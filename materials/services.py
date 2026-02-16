import stripe
from django.conf import settings

# Установите secret key из настроек
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(name):
    """Создаёт продукт в Stripe и возвращает его ID."""
    product = stripe.Product.create(name=name)
    return product['id']

def create_stripe_price(product_id, amount, currency='rub'):
    """
    Создаёт цену для продукта.
    amount — в рублях (целое число), в Stripe передаётся в копейках.
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),  # переводим в копейки
        currency=currency,
    )
    return price['id']

def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """Создаёт сессию оформления платежа и возвращает объект сессии."""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session

def retrieve_stripe_session(session_id):
    """Получает информацию о сессии по её ID (для проверки статуса)."""
    return stripe.checkout.Session.retrieve(session_id)