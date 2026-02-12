from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModeratorOrReadOnly, IsOwnerOrModerator
from users.permissions import IsModerator


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
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator & ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]