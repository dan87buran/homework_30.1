from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModeratorOrReadOnly(BasePermission):
    """
    - Для небезопасных методов (POST, PUT, PATCH, DELETE) доступ разрешён **только модераторам**.
    - Безопасные методы (GET, HEAD, OPTIONS) доступны всем авторизованным пользователям.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOrModerator(BasePermission):
    """
    - Модератор может редактировать **любой** объект.
    - Обычный пользователь может редактировать **только свои** объекты (проверка ``obj.owner == request.user``).
    - Безопасные методы доступны всем авторизованным.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.groups.filter(name='Модераторы').exists():
            return True
        return obj.owner == request.user