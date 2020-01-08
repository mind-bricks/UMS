from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from oauthlib.common import generate_token
from oauth2_provider import (
    models,
    settings,
)

application_class = models.get_application_model()
access_token_class = models.get_access_token_model()
refresh_token_class = models.get_refresh_token_model()


def verify(access_token):
    access_token = access_token_class.objects.select_related(
        'user',
        'application',
        'application__user',
    ).filter(
        Q(token=access_token) &
        Q(expires__gt=timezone.now()) &
        (
            Q(user__isnull=False) |
            Q(application__isnull=False)
        )
    ).first()
    if not access_token:
        return None, None

    return (
        (
            access_token.user or
            access_token.application.user
        ),
        access_token
    )


def grant(
        user,
        scopes=(),
        application=None,
        expire=settings.oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
):
    scopes = frozenset(scopes)
    expire = timezone.now() + timedelta(seconds=expire)
    access_token = access_token_class(
        user=user,
        token=generate_token(),
        application=application,
        scope=' '.join(scopes),
        expires=expire,
    )
    access_token.save()

    # create refresh token if application is available
    refresh_token = refresh_token_class(
        user=user,
        token=generate_token(),
        application=application,
        access_token=access_token,
    )
    refresh_token.save()

    return access_token, refresh_token
