from django.urls import (
    include,
    path,
)
from rest_framework_extensions import (
    routers,
)

from .views import (
    UserViewSet,
    GroupViewSet,
    PermissionViewSet,
)

router = routers.ExtendedDefaultRouter()
router_user = router.register(
    'users',
    UserViewSet,
    basename='users',
)
router_group = router.register(
    'groups',
    GroupViewSet,
    basename='groups',
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
