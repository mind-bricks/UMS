from django.apps import AppConfig


class AppConfig4Users(AppConfig):
    name = 'apps.users'
    label = 'users'


class AppConfig4OAuth(AppConfig):
    name = 'apps.oauth'
    label = 'oauth'
