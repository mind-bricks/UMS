import os
import json

from rest_framework import (
    reverse,
    status,
    test,
)


class OAuthTest(test.APITestCase):
    fixtures = [
        os.path.join('fixtures', 'users.json'),
        os.path.join('fixtures', 'oauth.json'),
    ]

    def test_oauth_introspect(self):
        url_token = reverse.reverse('oauth:token')
        url_introspection = reverse.reverse('oauth:introspect')
        # login system by oauth2 proto first
        response = self.client.post(url_token, {
            'grant_type': 'client_credentials',
            'client_id': 'L8GNY78qYX1caGrsGw0mwh70ZSuqSbBtY3013jgX',
            'client_secret':
                'h3uIhoazt4AuRW5yGowcjdKu3nUrvxsJUA0zIosvieRwpGGT8tUxD49KpNor'
                '79Ju7oVjcfVM1uwhDybC8aSJleWwkOh2pqMA2W9JgyZdtnDwKxCKZ1zVdGHP'
                '9H3XRFy4',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content.decode('utf8'))
        self.assertIn('access_token', response_data)
        access_token_sys = response_data.get('access_token')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(access_token_sys))
        response = self.client.post(
            url_introspection, {'token': access_token_sys})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exp', response.data)
        self.assertIn('scope', response.data)
        self.assertIn('user', response.data)
