from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    ''' Проверка является лиюзер админом'''
    #def has_object_permission(self, request, **kwargs):
    #    return (
    #        request.method in permissions.SAFE_METHODS
    #        or request.user == User.is_staf
    #    )
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)
    
    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)

        )
    
class IsAdminOrRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser))
        
    
class IsAdminOrUserOrRead(permissions.BasePermission):
    ''' Проверка является ли юзер админом'''
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_moderator
            or request.user.is_user)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_moderator
            or request.user.is_user))

class IsAuthOrAdminOrModerOrRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user == obj.author:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_moderator)

class IsAdminNoRead(permissions.BasePermission):
    ''' Проверка является лиюзер админом'''
    #def has_object_permission(self, request, **kwargs):
    #    return (
    #        request.method in permissions.SAFE_METHODS
    #        or request.user == User.is_staf
    #    )
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
            or request.user.is_staff)

