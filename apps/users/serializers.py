from rest_framework import serializers

from .models import (
    User,
    Group,
    Permission,
    ContentType,
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
        return Permission.objects.create(
            name=name,
            codename=name,
            content_type=ContentType.objects.get_for_model(User),
        )

    def update(self, instance, validated_data):
        raise AssertionError('not allowed')
