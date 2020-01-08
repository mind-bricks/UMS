from django.db.models import (
    ForeignKey,
    CASCADE,
)
from oauth2_provider import (
    models,
)


class Application(models.AbstractApplication):
    objects = models.ApplicationManager()


class Grant(models.AbstractGrant):
    pass


class AccessToken(models.AbstractAccessToken):
    pass


class RefreshToken(models.AbstractRefreshToken):
    application = ForeignKey(
        Application,
        null=True,
        on_delete=CASCADE,
    )
