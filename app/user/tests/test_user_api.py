from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user public apis"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """Test can create user with valid payload"""
        payload = {
            'email':'test@baratel.com',
            'password':'password1233',
            'name':'kangogo'
        }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_already_exists(self):
        """test cannot create existing user"""
        payload = {
            'email': 'test@baratel.com',
            'password': 'password1233'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test cannot create if password is less than 5 charcts"""
        payload = {
            'email': 'test@baratel.com',
            'password': 'pwd',
            'name':'sergon'
        }
        res = self.client.post(CREATE_USER_URL,payload)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test that a token is created for user"""
        payload = {
            'email':'hillary@baratel.com',
            'password':'password123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Token is not created if invalid credentials are provided"""
        create_user(email='kangogo@gmail.com',password='password')
        payload = {
            'email': 'kangogo@gmail.com',
            'password': 'wrong'
        }
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test token not created if user does not exist"""
        payload = {
            'email': 'kangogo@gmail.com',
            'password': 'wrong'
        }
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test that email and password are required"""
        payload = {
            'email': 'kangogo@gmail.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL,payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)



