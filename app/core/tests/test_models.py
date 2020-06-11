from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_userwithemail_succesfull(self):
        """Test create user with email succesfully"""
        email = 'hillergon@gmail.com'
        password = 'adminkangogo'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))



    def test_normalize_user_email(self):
        """test email for new user is nomalized"""
        email = 'kangogo@BARATEL.com'
        user = get_user_model().objects.create_user(email,'barazel')
        self.assertEqual(user.email,email.lower())

    def test_user_invalid_email(self):
        """test inavlid email fails"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'pass123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'kangogo@baatel.com',
            'mypassword')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
