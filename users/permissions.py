from rest_framework import permissions


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешение:
    - модератор может только просматривать и редактировать любые объекты;
    - обычный пользователь может работать только со своими объектами.
    """

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.is_authenticated and not request.user.groups.filter(name="Модераторы").exists()
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == "destroy":
            if request.user.groups.filter(name="Модераторы").exists():
                return False
            return obj.owner == request.user

        if view.action in ["retrieve", "update", "partial_update"]:
            if request.user.groups.filter(name="Модераторы").exists():
                return True
            return obj.owner == request.user

        return False
