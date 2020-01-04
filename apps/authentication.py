from django.db.models import Q
from django.utils import timezone
from oauth2_provider import models


def verify(access_token):
    access_token_class = models.get_access_token_model()
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


def grant(access_token):
    pass
