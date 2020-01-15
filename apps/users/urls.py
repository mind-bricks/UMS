from django.urls import (
    include,
    path,
)
from rest_framework_extensions import (
    routers,
)

from .views import (
    UserViewSet,
    UserGroupViewSet,
    UserPermissionViewSet,
    GroupViewSet,
    GroupPermissionViewSet,
    PermissionViewSet,
)

router = routers.ExtendedDefaultRouter()
router_user = router.register(
    'users',
    UserViewSet,
    basename='users',
)
router_user.register(
    'groups',
    UserGroupViewSet,
    basename='user-groups',
    parents_query_lookups=['user__uuid'],
)
router_user.register(
    'permissions',
    UserPermissionViewSet,
    basename='user-permissions',
    parents_query_lookups=['user__uuid'],
)
router_group = router.register(
    'groups',
    GroupViewSet,
    basename='groups',
)
router_group.register(
    'permissions',
    GroupPermissionViewSet,
    basename='group-permissions',
    parents_query_lookups=['group__name'],
)
router.register(
    'permissions',
    PermissionViewSet,
    basename='permissions',
)

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
]
