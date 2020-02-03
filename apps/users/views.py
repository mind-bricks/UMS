from django.db.models import Q
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    response,
    viewsets,
)
from rest_framework_extensions.mixins import (
    NestedViewSetMixin,
)

from ..permissions import (
    TokenHasScope,
)
from .access import (
    find_users,
    find_groups,
    find_permissions,
    find_user_permissions,
    get_user,
    get_group,
    get_permission,
)
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserPasswordSerializer,
    UserSignupSerializer,
    UserGroupSerializer,
    UserPermissionSerializer,
    GroupSerializer,
    GroupPermissionSerializer,
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
        methods=['get'],
        url_path='self/groups',
        url_name='self-groups',
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserGroupSerializer,
    )
    def self_groups(self, request):
        queryset = request.user.groups.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        methods=['get'],
        url_path='self/permissions',
        url_name='self-permissions',
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserPermissionSerializer,
    )
    def self_permissions(self, request):
        queryset = find_user_permissions(request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        methods=['post'],
        detail=False,
        serializer_class=UserSignupSerializer,
    )
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(realm=request.user.realm)
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

    @decorators.action(
        methods=['post'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserPasswordSerializer,
    )
    def password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)


class UserGroupViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'name'
    lookup_value_regex = '[^/]+'
    permission_classes = [TokenHasScope]
    queryset = find_groups()
    required_scopes = ['users.admin']
    serializer_class = UserGroupSerializer

    def perform_create(self, serializer):
        user = self.kwargs.get('parent_lookup_user__uuid')
        user = user and get_user(uuid=user)
        if not user:
            raise exceptions.NotFound('user not found')

        serializer.save(user=user)

    def perform_destroy(self, instance):
        user = self.kwargs.get('parent_lookup_user__uuid')
        user = user and get_user(uuid=user)
        if not user:
            raise exceptions.NotFound('user not found')

        user.groups.remove(instance)


class UserPermissionViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'codename'
    lookup_value_regex = '[^/]+'
    permission_classes = [TokenHasScope]
    required_scopes = ['users.admin']
    serializer_class = UserPermissionSerializer

    @property
    def queryset(self):
        return find_permissions()

    def perform_create(self, serializer):
        user = self.kwargs.get('parent_lookup_user__uuid')
        user = user and get_user(uuid=user)
        if not user:
            raise exceptions.NotFound('user not found')

        serializer.save(user=user)

    def perform_destroy(self, instance):
        user = self.kwargs.get('parent_lookup_user__uuid')
        user = user and get_user(uuid=user)
        if not user:
            raise exceptions.NotFound('user not found')

        user.user_permissions.remove(instance)


class GroupViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'name'
    lookup_value_regex = '[^/]+'
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


class GroupPermissionViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'codename'
    lookup_value_regex = '[^/]+'
    permission_classes = [TokenHasScope]
    required_scopes = ['groups.admin']
    serializer_class = GroupPermissionSerializer

    @property
    def queryset(self):
        return find_permissions()

    def perform_create(self, serializer):
        group = self.kwargs.get('parent_lookup_group__name')
        group = group and get_group(name=group)
        if not group:
            raise exceptions.NotFound('user not found')

        serializer.save(group=group)

    def perform_destroy(self, instance):
        group = self.kwargs.get('parent_lookup_group__name')
        group = group and get_group(name=group)
        if not group:
            raise exceptions.NotFound('user not found')

        group.permissions.remove(instance)


class PermissionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'codename'
    lookup_value_regex = '[^/]+'
    permission_classes = [TokenHasScope]
    required_scopes = ['permissions.admin']
    serializer_class = PermissionSerializer

    @property
    def queryset(self):
        return find_permissions()

    def perform_destroy(self, instance):
        if get_permission(
                (
                    Q(user__isnull=False) |
                    Q(group__isnull=False)
                ) & Q(id=instance.id)
        ):
            raise exceptions.NotAcceptable('permission is referenced')
        instance.delete()
