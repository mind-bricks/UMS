from django.conf import settings

USERS_LOGIN_EXPIRE = getattr(settings, 'USERS_LOGIN_EXPIRE', int(3600 * 10))
