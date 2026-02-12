from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModerator(BasePermission):
    """
    Разрешение, предоставляющее доступ только пользователям,
    состоящим в группе 'Модераторы'.

    Группа создаётся через фикстуру или кастомную команду.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Модераторы').exists()


class IsOwner(BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его владельцу.

    Предполагается, что у модели есть поле ``owner``, ссылающееся на :model:`users.User`.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user