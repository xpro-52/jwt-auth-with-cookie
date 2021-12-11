from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.contrib.auth import get_user_model, login
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from typing import Any


USER = get_user_model()


class RegisterTest(TestCase):
    def test_register(self):
        data = {'username': 'test', 
                'email': 'test@example.com',
                'password': 'testpass'}
        resp = self.client.post(reverse('register'), data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(USER.objects.first())

        created_user_dict = USER.objects.first().__dict__
        for key in ['id', 'username', 'email']:
            user_db_data_str = str(created_user_dict[key])
            with self.subTest(key=key):
                if key != 'id':
                    self.assertEqual(user_db_data_str, data[key])
                self.assertEqual(resp.data[key], user_db_data_str)


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        USER.objects.create_user(username='test',
                                 email='email@example.com',
                                 password='testpass')  # create_userをつかう createだとstatus_code=401
    
    def _login_process(self) -> tuple[APIClient, (Any | WSGIRequest)]:
        client = APIClient()
        return client, client.post(reverse('login'),
                                   data={'username': 'test', 'password': 'testpass'},
                                   format='json')

    def test_login(self):
        client, resp = self._login_process()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(client.cookies.get('access'))
        self.assertIsNotNone(client.cookies.get('refresh'))

    def test_user_info(self):
        client, _ = self._login_process()
        resp = client.get(reverse('user_info'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ['id', 'username', 'email']:
            with self.subTest(key=key):
                self.assertEqual(resp.data[key], 
                                 str(USER.objects.first().__dict__[key]))

    def logout(self):
        client, _ = self._login_process()
        resp = client.post(reverse('logout'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(client.cookies)
