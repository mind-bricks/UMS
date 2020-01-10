from django.utils.translation import ugettext_lazy as _
from oauth2_provider import scopes
from rest_framework import (
    authentication,
    exceptions,
)

from .access import (
    find_permissions,
    find_user_permissions,
)
from .authentication import (
    verify as auth_verify,
)


class SettingsScopes(scopes.BaseScopes):

    def get_all_scopes(self):
        return [perm.codename for perm in find_permissions()]

    def get_available_scopes(
            self,
            application=None,
            request=None,
            *args,
            **kwargs
    ):
        user = application and application.user
        return [
            perm.codename
            for perm in find_user_permissions(user)
        ] if user else []

    def get_default_scopes(
            self,
            application=None,
            request=None,
            *args,
            **kwargs
    ):
        return self.get_available_scopes(
            application,
            request,
            *args,
            **kwargs
        )


class SettingsAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = _(
                'Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _(
                'Invalid token header. '
                'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                'Invalid token header. '
                'Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        credentials = self.authenticate_credentials(token)
        if not credentials:
            msg = _('Invalid token.')
            raise exceptions.AuthenticationFailed(msg)

        return (
            credentials[0],
            credentials[1],
        )

    @staticmethod
    def authenticate_credentials(key):
        user, auth = auth_verify(key)
        return auth and (user, auth)

    def authenticate_header(self, request):
        return 'Bearer'
