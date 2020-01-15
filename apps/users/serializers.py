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
    create_group,
    create_permission,
    get_user,
    get_group,
    get_permission,
)
from .models import (
    User,
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
            is_active=True,
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
            'refresh_token': refresh_token.token,
            'expires_in': USERS_LOGIN_EXPIRE,
        }

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=128,
        write_only=True,
    )
    password_new = serializers.CharField(
        max_length=128,
        write_only=True,
    )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request and request.user
        if not user:
            raise AssertionError('user not found')

        if not user.check_password(validated_data['password']):
            raise exceptions.AuthenticationFailed(
                'incorrect password'
            )

        user.set_password(validated_data['password_new'])
        user.save(update_fields=['password'])
        return user

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class UserSignupSerializer(serializers.Serializer):

    def create(self, validated_data):
        raise AssertionError('not allowed')

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class UserGroupSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        name = validated_data['name']
        user = validated_data['user']
        group = get_group(name=name)
        if not group:
            raise exceptions.ValidationError('invalid group')

        user.groups.add(group)
        return group

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class UserPermissionSerializer(serializers.Serializer):
    name = serializers.CharField(
        source='codename',
    )

    def create(self, validated_data):
        name = validated_data['codename']
        user = validated_data['user']
        permission = get_permission(codename=name)
        if not permission:
            raise exceptions.ValidationError('invalid permission')

        user.user_permissions.add(permission)
        return permission

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class GroupSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        name = validated_data['name']
        instance = create_group(name=name)
        if not instance:
            raise exceptions.ValidationError('duplicated group')
        return instance

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class GroupPermissionSerializer(serializers.Serializer):
    name = serializers.CharField(
        source='codename',
    )

    def create(self, validated_data):
        name = validated_data['codename']
        group = validated_data['group']
        permission = get_permission(codename=name)
        if not permission:
            raise exceptions.ValidationError('invalid permission')

        group.permissions.add(permission)
        return permission

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')


class PermissionSerializer(serializers.Serializer):
    name = serializers.CharField(
        source='codename',
    )
    description = serializers.CharField(
        source='name',
        required=False,
    )

    def create(self, validated_data):
        name = validated_data['codename']
        name = name.lower()
        name = name.strip()
        name = name.replace(' ', '|')
        description = validated_data.get('description') or name
        instance = create_permission(
            codename=name,
            name=description,
        )
        if not instance:
            raise exceptions.ValidationError(
                'duplicated permission')
        return instance

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')
