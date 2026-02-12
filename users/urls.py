from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserCreateView, UserDetailView, PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    # Регистрация и профиль
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', UserDetailView.as_view(), name='profile'),

    # JWT-токены
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Платежи
    path('', include(router.urls)),
]