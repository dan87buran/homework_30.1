from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonListCreateView,
    LessonRetrieveUpdateDestroyView,
    SubscriptionAPIView
)
from .views import PaymentCreateView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateView.as_view()),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view()),
    path('subscriptions/', SubscriptionAPIView.as_view()),
path('payments/', PaymentCreateView.as_view(), name='payment-create'),

]
