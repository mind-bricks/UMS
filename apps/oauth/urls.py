from django.urls import (
    # include,
    path,
)

from .views import (
    AuthorizationView,
    RevokeTokenView,
    TokenView,
    IntrospectTokenView
)

app_name = 'oauth'

urlpatterns = [
    path('authorize/', AuthorizationView.as_view(), name='authorize'),
    path('token/', TokenView.as_view(), name='token'),
    path('revoke_token/', RevokeTokenView.as_view(), name='revoke-token'),
    path('introspect/', IntrospectTokenView.as_view(), name='introspect'),
]
