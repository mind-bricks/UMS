from os import path

from rest_framework import (
    reverse,
    status,
    test,
)


class UserPreLoginTest(test.APITestCase):
    def test_signup_user(self):
        pass


class UserPostLoginTest(test.APITestCase):
    fixtures = [
        path.join('fixtures', 'test_users.json')
    ]

    def setUp(self):
        url_login = reverse.reverse('users:users-login')
        response = self.client.post(url_login, data={
            'username': 'test_user',
            'password': 'abcdefgh',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('expires_in', response.data)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(
            response.data.get('access_token')))

    def test_retrieve_user_self(self):
        url_self = reverse.reverse('users:users-self')
        response = self.client.get(url_self)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'test_user')

    def test_update_user_self(self):
        url_self = reverse.reverse('users:users-self')
        response = self.client.patch(url_self, data={
            'first_name': 'new first name',
            'last_name': 'new last name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), 'new first name')
        self.assertEqual(response.data.get('last_name'), 'new last name')
