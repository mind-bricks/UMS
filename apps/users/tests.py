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
        path.join('fixtures', 'users.json'),
        path.join('fixtures', 'test_users.json'),
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


class AdminTest(test.APITestCase):
    access_token_of_admin = None
    access_token_of_user = None
    fixtures = [
        path.join('fixtures', 'users.json'),
        path.join('fixtures', 'test_users.json'),
    ]

    @classmethod
    def setUpTestData(cls):
        url_login = reverse.reverse('users:users-login')
        client = cls.client_class()
        response = client.post(url_login, data={
            'username': 'test_admin',
            'password': 'abcdefgh',
        })
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('access_token', response.data)
        # self.assertIn('refresh_token', response.data)
        # self.assertIn('expires_in', response.data)
        cls.access_token_of_admin = response.data.get('access_token')

        response = client.post(url_login, data={
            'username': 'test_user',
            'password': 'abcdefgh',
        })
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn('access_token', response.data)
        # self.assertIn('refresh_token', response.data)
        # self.assertIn('expires_in', response.data)
        cls.access_token_of_user = response.data.get('access_token')


class UserAdminTest(AdminTest):

    def test_list_user(self):
        url_list = reverse.reverse('users:users-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_retrieve_user(self):
        url_detail = reverse.reverse(
            'users:users-detail', ['dc9b60b8-3115-11ea-bbc8-a86bad54c153'])

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'test_admin')
        self.assertEqual(response.data.get('first_name'), 'admin_first_name')
        self.assertEqual(response.data.get('last_name'), 'admin_last_name')


class GroupAdminTest(AdminTest):
    def test_list_group(self):
        url_list = reverse.reverse('users:groups-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)

    def test_create_group(self):
        url_list = reverse.reverse('users:groups-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(url_list, data={'name': 'test_group_2'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url_list, data={'name': 'test_group_2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_group(self):
        url_detail_1 = reverse.reverse('users:groups-detail', ['test_group'])
        url_detail_2 = reverse.reverse('users:groups-detail', ['superuser'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)


class PermissionAdminTest(AdminTest):
    def test_list_permission(self):
        url_list = reverse.reverse('users:permissions-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 9)

    def test_create_permission(self):
        url_list = reverse.reverse('users:permissions-list')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.post(url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.post(
            url_list, data={'name': 'test.permission_2'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            url_list, data={'name': 'test.permission_2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_permission(self):
        url_detail_1 = reverse.reverse(
            'users:permissions-detail', ['test_permission'])
        url_detail_2 = reverse.reverse(
            'users:permissions-detail', ['users.admin'])
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_user))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.access_token_of_admin))
        response = self.client.delete(url_detail_1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(url_detail_2)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
