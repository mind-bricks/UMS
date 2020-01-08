from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import (
    exceptions,
    serializers,
)

from ..authentication import (
    grant as auth_grant,
)
from .access import (
    create_permission,
    get_user,
)
from .models import (
    User,
    Group,
)
from .settings import (
    USERS_LOGIN_EXPIRE,
)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='realm_username',
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'uuid',
            'realm',
            'username',
            'email',
            'mobile',
            'first_name',
            'last_name',
            'date_joined',
        ]
        read_only_fields = [
            'uuid',
            'realm',
            'username',
            'email',
            'mobile',
            'date_joined',
        ]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'name',
        ]


class PermissionSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        name = validated_data['name']
        name = name.lower()
        name = name.strip()
        name = name.replace(' ', '.')
        return create_permission(
            name=name,
            codename=name,
        )

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class UserLoginSerializer(serializers.Serializer):
    realm = serializers.CharField(
        max_length=32,
        write_only=True,
        default='',
        allow_blank='',
        required=False,
    )
    username = serializers.CharField(
        max_length=128,
        write_only=True,
    )
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        default='',
        required=False,
    )
    access_token = serializers.CharField(
        max_length=64,
        read_only=True,
    )
    refresh_token = serializers.CharField(
        max_length=64,
        read_only=True,
    )
    expires_in = serializers.IntegerField(
        read_only=True,
    )

    def create(self, validated_data):
        user = get_user(
            realm=validated_data['realm'],
            realm_username=validated_data['username'],
        )
        if (
                not user or
                not user.check_password(validated_data['password'])
        ):
            raise exceptions.AuthenticationFailed(
                _('username or password error'),
                'username or password error'
            )

        access_token, refresh_token = auth_grant(
            user,
            expire=USERS_LOGIN_EXPIRE,
        )

        # update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return {
            'access_token': access_token.token,
            'refresh_token': refresh_token and refresh_token.token,
            'expires_in': USERS_LOGIN_EXPIRE,
        }

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')
