__all__ = [
    'User',
    'Group',
    'Permission',
    'ContentType',
]

from uuid import uuid1

from django.contrib.auth.models import (
    AbstractUser,
    Group,
    Permission,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    uuid = models.UUIDField(
        unique=True,
        default=uuid1,
    )
    realm = models.CharField(
        max_length=32,
        blank=True,
        default='',
    )
    realm_username = models.CharField(
        max_length=128,
        validators=[AbstractUser.username_validator],
    )
    email = models.EmailField(
        _('email address'),
        blank=True,
        null=True,
        default=None,
    )
    mobile = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        default=None,
    )

    class Meta:
        unique_together = [
            ('realm', 'realm_username'),
            ('realm', 'email'),
            ('realm', 'mobile'),
        ]
