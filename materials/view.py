from rest_framework import generics, status
from rest_framework.response import Response
from .models import Course, Lesson, Payment
from .serializers import PaymentSerializer
from .services import create_stripe_product, create_stripe_price, create_stripe_checkout_session
from rest_framework.views import APIView
from .services import retrieve_stripe_session

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')
        lesson_id = request.data.get('lesson')
        amount = request.data.get('amount')

        # Проверяем, что указан хотя бы курс или урок
        if not course_id and not lesson_id:
            return Response({'error': 'Укажите course или lesson'}, status=status.HTTP_400_BAD_REQUEST)

        # Определяем название для продукта (можно взять из названия курса/урока)
        if course_id:
            obj = Course.objects.get(id=course_id)
            product_name = f"Курс: {obj.title}"
        else:
            obj = Lesson.objects.get(id=lesson_id)
            product_name = f"Урок: {obj.title}"

        # Создаём продукт и цену в Stripe
        try:
            product_id = create_stripe_product(product_name)
            price_id = create_stripe_price(product_id, amount)
            # success_url и cancel_url должны вести на ваш фронтенд или просто на страницу подтверждения
            success_url = "http://localhost:8000/api/payment/success/"
            cancel_url = "http://localhost:8000/api/payment/cancel/"
            session = create_stripe_checkout_session(price_id, success_url, cancel_url)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Сохраняем платёж в БД
        payment = Payment.objects.create(
            user=user,
            course_id=course_id,
            lesson_id=lesson_id,
            amount=amount,
            session_id=session['id'],
            payment_url=session['url'],
            status='pending'
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PaymentStatusView(APIView):
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Платёж не найден'}, status=status.HTTP_404_NOT_FOUND)

        session = retrieve_stripe_session(payment.session_id)
        # Статус платежа из Stripe: session.payment_status может быть 'paid', 'unpaid', 'no_payment_required'
        if session.payment_status == 'paid':
            payment.status = 'paid'
            payment.save()
        return Response({'status': payment.status, 'stripe_status': session.payment_status})