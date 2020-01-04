from django.contrib import admin
from django.urls import (
    include,
    path,
)
from rest_framework_swagger import (
    views as swagger_views
)

urlpatterns = [
    path('', include('apps.users.urls')),
    path('oauth2/', include('apps.oauth.urls')),
    path('admin/', admin.site.urls),
    path('swagger/', swagger_views.get_swagger_view(title='UMS APIs')),
]
