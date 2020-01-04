__all__ = [
    'AuthorizationView',
    'RevokeTokenView',
    'TokenView',
    'IntrospectTokenView',
]

from calendar import timegm

from oauth2_provider.views import (
    AuthorizationView,
    RevokeTokenView,
    TokenView,
)
from rest_framework import (
    generics,
    response,
    status,
)

from ..authentication import verify as auth_verify
from ..permissions import TokenHasScope
from .serializers import IntrospectTokenSerializer


class IntrospectTokenView(generics.GenericAPIView):
    permission_classes = [TokenHasScope]
    serializer_class = IntrospectTokenSerializer
    required_scopes = ['introspection']

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, access_token = auth_verify(
            serializer.validated_data['token'])
        if not access_token:
            return response.Response(
                {'error': 'user not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer.save(
            exp=int(timegm(access_token.expires.utctimetuple())),
            scope=access_token.scope,
            user={
                'uuid': user.uuid,
                'username': user.realm_username,
                'realm': user.realm,
            },
        )
        return response.Response(serializer.data)
