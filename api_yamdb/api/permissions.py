from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
            )
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_admin
        )


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser
            or request.user.is_admin
        )


class AuthorOrHasRoleOrReadOnly(permissions.BasePermission):
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
            or obj.author == request.user
        )


class ReviewAndCommentPermission(permissions.BasePermission):
    """
    Разрешение оставлять отзывы и комментировать
    для зарегистрированных пользователей.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS) or (
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        if request.method == 'PATCH' or request.method == 'DELETE':
            return (
                request.user.role == 'admin'
                or request.user.role == 'moderator'
                or obj.author == request.user
            )
        return False
