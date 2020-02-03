__all__ = [
    'create_permission',
    'create_user',
    'create_group',
    'get_permission',
    'get_user',
    'get_group',
    'find_permissions',
    'find_user_permissions',
    'find_users',
    'find_groups',
]

from django.db import IntegrityError

from ..access import (
    create_permission,
    get_permission,
    find_permissions,
    find_user_permissions,
)
from .models import (
    User,
    Group,
)


def create_user(username=None, password=None, **kwargs):
    try:
        assert username is not None
        assert password is not None
        instance = User(username=username, **kwargs)
        instance.set_password(password)
        instance.save()
        return instance
    except IntegrityError:
        return None


def get_user(**kwargs):
    return User.objects.filter(**kwargs).first()


def find_users(**kwargs):
    return User.objects.filter(**kwargs).all()


def create_group(**kwargs):
    try:
        instance = Group(**kwargs)
        instance.save()
        return instance
    except IntegrityError:
        return None


def get_group(**kwargs):
    return Group.objects.filter(**kwargs).first()


def find_groups(**kwargs):
    return Group.objects.filter(**kwargs).all()
