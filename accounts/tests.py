from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.user_data = {
            'name': 'Dr. Alice Carter',
            'email': 'alice.carter@hospital.com',
            'password': 'StrongPassword123!',
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], self.user_data['email'].lower())
        self.assertTrue(User.objects.filter(email=self.user_data['email'].lower()).exists())

    def test_register_user_duplicate_email(self):
        # First registration
        self.client.post(self.register_url, self.user_data)
        # Duplicate registration
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_missing_fields(self):
        response = self.client.post(self.register_url, {'email': 'incomplete@test.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        # Register first
        self.client.post(self.register_url, self.user_data)

        # Login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'].lower())

    def test_login_user_invalid_password(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_nonexistent_email(self):
        login_data = {
            'email': 'nobody@hospital.com',
            'password': 'SomePassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
