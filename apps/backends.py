from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from oauth2_provider import scopes
from rest_framework import authentication, exceptions

from .authentication import verify as auth_verify


class SettingsScopes(scopes.BaseScopes):

    @cached_property
    def content_type(self):
        return ContentType.objects.get_for_model(get_user_model())

    def get_all_scopes(self):
        return [
            perm.codename
            for perm in Permission.objects.filter(
                content_type=self.content_type,
            ).all()
        ]

    def get_available_scopes(
            self,
            application=None,
            request=None,
            *args,
            **kwargs
    ):
        user = application and application.user
        return user and [
            perm.codename
            for perm in Permission.objects.filter(
                Q(content_type=self.content_type) &
                (
                    Q(user=user) |
                    Q(group_set__user=user)
                )
            ).all()
        ] or []

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
        if not auth or auth[0].lower() != 'bearer':
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
        return (
            credentials and
            (
                credentials[0],
                credentials[1],
            )
        )

    @staticmethod
    def authenticate_credentials(key):
        user, auth = auth_verify(key)
        return auth and (user, auth)

    def authenticate_header(self, request):
        return 'Bearer'
