from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions


class TokenHasScope(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

    def has_permission(self, request, view):
        token = request.auth
        if not token:
            return False

        required_scopes = self.get_scopes(request, view)
        # no required scopes found
        if not required_scopes:
            return True

        if token.application:
            # for oauth2 login
            return any(
                token.allow_scopes(required_scope.split())
                for required_scope in required_scopes
            )

        else:
            # for normal login
            return any(
                request.user.has_perms(required_scope.split())
                for required_scope in required_scopes
            )

    def get_scopes(self, request, view):
        try:
            return getattr(view, 'required_scopes')
        except AttributeError:
            raise ImproperlyConfigured(
                'TokenHasScope requires the view to define '
                'the required_scopes attribute'
            )
