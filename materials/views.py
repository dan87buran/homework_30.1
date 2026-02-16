from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from users.permissions import IsModerator
from .models import Course, Lesson, Subscription, Payment
from .paginators import StandardResultsSetPagination
from .permissions import IsOwnerOrModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.all().order_by('id')
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]


class SubscriptionAPIView(APIView):
    schema = None  # <--- КЛЮЧЕВАЯ СТРОКА

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)
        if subscription.exists():
            subscription.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'
        return Response({'message': message})


class PaymentCreateView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer