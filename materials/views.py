from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsModerator
from .models import Course, Subscription
from .models import Lesson
from .paginators import StandardResultsSetPagination
from .permissions import IsOwnerOrModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CourseViewSet(ModelViewSet):
    """
    ViewSet для модели :model:`materials.Course`.

    **Права доступа:**
    * Создание курса — только **авторизованные пользователи**, **НЕ модераторы** (модераторам запрещено).
    * Просмотр списка и деталей — все авторизованные.
    * Редактирование — модераторы (любые) и владельцы курса.
    * Удаление — только владельцы (модераторам запрещено).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Динамическое назначение прав в зависимости от action.
        """
        if self.action == 'create':
            # Создавать могут только авторизованные пользователи, НЕ модераторы
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактировать могут модераторы ИЛИ владельцы
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            # Удалять могут только владельцы (модераторам нельзя)
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator & ~IsModerator]
        else:
            # list, retrieve — только авторизованные
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Автоматически присваиваем владельца при создании курса.
        """
        serializer.save(owner=self.request.user)


class LessonListCreateView(ListCreateAPIView):
    """
    Представление для получения списка уроков и создания нового урока.

    **Права доступа:**
    * GET (список) — все авторизованные.
    * POST (создание) — только **не-модераторы** (модераторам запрещено создавать).
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        При создании урока автоматически проставляем владельца.
        """
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра, редактирования и удаления одного урока.

    **Права доступа:**
    * GET — все авторизованные.
    * PUT/PATCH — модераторы или владельцы.
    * DELETE — только владельцы (модераторам запрещено).
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]  # исправлено!
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

class SubscriptionAPIView(APIView):
    """
    POST-запрос с параметром course_id:
    - если подписка есть – удаляет её,
    - если нет – создаёт.
    """
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

class CourseViewSet(ModelViewSet):

    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]   # если ~ работает, иначе замените на отдельный permission
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]        # исправлено!
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in self.permission_classes]

class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.all().order_by('id')
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination