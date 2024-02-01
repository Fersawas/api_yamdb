from rest_framework.permissions import BasePermission
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class IsAdminOrRead(permissions.BasePermission):
    ''' Проверка является лиюзер админом'''
    def has_object_permission(self, request):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == User.is_staf
        )
