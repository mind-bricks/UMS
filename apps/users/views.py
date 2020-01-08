from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    response,
    viewsets,
)

from ..permissions import (
    TokenHasScope,
)
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'uuid'
    permission_classes = [TokenHasScope]
    required_scopes = ['users.write']
    serializer_class = UserSerializer

    @decorators.action(
        methods=['get', 'patch'],
        url_path='self',
        url_name='self',
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def self(self, request):
        method_name = '{}_self'.format(request.method.lower())
        method = getattr(self, method_name, None)
        if not method:
            raise exceptions.NotFound()
        return method(request)

    def get_self(self, request):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    def patch_self(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    @decorators.action(
        methods=['post'],
        detail=False,
        permission_classes=[],
        serializer_class=UserLoginSerializer,
    )
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)
