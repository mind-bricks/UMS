from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import (
    exceptions,
    response,
    views,
)


class ExceptionHandler(object):

    def parse_as_list(self, exec_detail):
        details = [self.parse(d) for d in exec_detail if d]
        return details[0] if len(details) == 1 else {
            'error_description': details,
            'error': 'multiple errors'
        }

    def parse_as_dict(self, exec_detail):
        details = [
            (k, self.parse(d)) for k, d in exec_detail.items() if d]
        return {
            'error_description': details[0][1],
            'error': details[0][0]
        } if len(details) == 1 else {
            'error_description': [
                {
                    'error_description': v[1],
                    'error': v[0],
                } for v in details
            ],
            'error': 'multiple errors'
        }

    def parse(self, exec_detail):
        if not exec_detail:
            return exec_detail

        if isinstance(exec_detail, list):
            return self.parse_as_list(exec_detail)

        if isinstance(exec_detail, dict):
            return self.parse_as_dict(exec_detail)

        return {
            'error_description': exec_detail,
            'error': exec_detail.code
        }

    def __call__(self, exc, context):
        if isinstance(exc, Http404):
            exc = exceptions.NotFound()
        elif isinstance(exc, PermissionDenied):
            exc = exceptions.PermissionDenied()

        if isinstance(exc, exceptions.APIException):
            headers = {}

            exec_auth_header = getattr(exc, 'auth_header', None)
            if exec_auth_header:
                headers['WWW-Authenticate'] = exec_auth_header

            exec_wait = getattr(exc, 'wait', None)
            if exec_wait:
                headers['Retry-After'] = '%d' % exec_wait

            views.set_rollback()

            return response.Response(
                self.parse(exc.detail),
                status=exc.status_code,
                headers=headers,
            )

        return None


default_handler = ExceptionHandler()
