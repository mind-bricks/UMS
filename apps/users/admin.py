from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as _UserAdmin,
    UserCreationForm as _UserCreationForm,
)
from django.contrib.auth.forms import UsernameField
from django.forms import CharField
from django.utils.translation import gettext_lazy as _

from .models import User


class UserCreationForm(_UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'realm',
            'realm_username',
        )
        field_classes = {
            'username': UsernameField,
            'realm': CharField,
            'realm_username': UsernameField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserAdmin(_UserAdmin):
    fieldsets = (
        (None, {'fields': (
            'username',
            'realm',
            'realm_username',
            'password',
        )}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'email',
            'mobile',
        )}),
        (_('Permissions'), {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
        (_('Important dates'), {'fields': (
            'last_login',
            'date_joined',
        )}),
    )
    list_display = (
        'username',
        'realm',
        'realm_username',
        'email',
        'mobile',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
    )
    search_fields = (
        'realm',
        'realm_username',
        'username',
        'first_name',
        'last_name',
        'email',
        'mobile',
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': (
            'username',
            'realm',
            'realm_username',
            'password1',
            'password2',
        )}),
    )
    add_form = UserCreationForm


admin.site.register(User, UserAdmin)
