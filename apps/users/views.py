from django.db.models import Q
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    response,
    viewsets,
)
# from rest_framework_extensions.mixins import (
#     NestedViewSetMixin,
# )

from ..permissions import (
    TokenHasScope,
)
from .access import (
    find_users,
    find_groups,
    find_permissions,
    get_group,
    get_permission,
)
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    GroupSerializer,
    PermissionSerializer,
)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'uuid'
    permission_classes = [TokenHasScope]
    queryset = find_users()
    required_scopes = ['users.admin']
    serializer_class = UserSerializer

    @decorators.action(
        methods=['get', 'patch'],
        url_path='self',
        url_name='self',
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
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


class GroupViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'name'
    permission_classes = [TokenHasScope]
    queryset = find_groups()
    required_scopes = ['groups.admin']
    serializer_class = GroupSerializer

    def perform_destroy(self, instance):
        if get_group(
                id=instance.id,
                user__isnull=False,
        ):
            raise exceptions.NotAcceptable('group is referenced')
        instance.delete()


class PermissionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'codename'
    lookup_value_regex = '[^/]+'
    permission_classes = [TokenHasScope]
    queryset = find_permissions()
    required_scopes = ['permissions.admin']
    serializer_class = PermissionSerializer

    def perform_destroy(self, instance):
        if get_permission(
                (
                    Q(user__isnull=False) |
                    Q(group__isnull=False)
                ) & Q(id=instance.id)
        ):
            raise exceptions.NotAcceptable('permission is referenced')
        instance.delete()


class UserGroupViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'name'
