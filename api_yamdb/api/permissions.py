from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверка является лиюзер админом"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin
                 or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrRead(permissions.BasePermission):
    """Проверка является лиюзер админом
    с доступом к просмотру без регистрации
    и смс"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class IsAdminOrUserOrRead(permissions.BasePermission):
    """Проверка является ли юзер админом
    или одним из аутунтифицированных пользвателей"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_moderator
                or request.user.is_user
            )
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_moderator
                or request.user.is_user
            )
        )


class IsAdminNoRead(permissions.BasePermission):
    """Проверка является лиюзер админом без доступа к просмотру"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_staff
        )


class IsStaffOrAuthorOrReadOnly(permissions.BasePermission):
    """Проверка прав для отзывов и комментариев."""

    message = "Нужны права администратора/модератора или автора"

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )
