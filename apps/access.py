from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Q


def create_permission(**kwargs):
    try:
        instance = Permission(
            content_type=ContentType.objects.get_for_model(Permission),
            **kwargs
        )
        instance.save()
        return instance
    except IntegrityError:
        return None


def get_permission(*args, **kwargs):
    return Permission.objects.filter(
        *args,
        content_type=ContentType.objects.get_for_model(Permission),
        **kwargs
    ).first()


def find_permissions(*args, **kwargs):
    return Permission.objects.filter(
        *args,
        content_type=ContentType.objects.get_for_model(Permission),
        **kwargs
    ).distinct().all()


def find_user_permissions(user):
    return find_permissions(Q(user=user) | Q(group__user=user))
