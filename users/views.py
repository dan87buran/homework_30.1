from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer
from .permissions import IsModerator


class UserCreateView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.

    **Доступ:** любой (неавторизованный).
    **Шаблон:** не используется (API).
    **Context:** отсутствует.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # открыто для всех


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление профиля пользователя.

    **Доступ:** только авторизованный пользователь может видеть/редактировать свой профиль.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Возвращает текущего авторизованного пользователя."""
        return self.request.user


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с платежами.

    **Доступ:**
    * Только авторизованные пользователи.
    * Модераторы имеют полный доступ.
    * Обычные пользователи видят только свои платежи.

    **Фильтрация:** по курсу, уроку, способу оплаты.
    **Сортировка:** по дате оплаты.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Модераторы видят все платежи, обычные пользователи — только свои."""
        if IsModerator().has_permission(self.request, self):
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)