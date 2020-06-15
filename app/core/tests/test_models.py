
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .. import models


def sample_user(email='kangogo@baratel.com',password='password123',name='kangogo'):
    """create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_userwithemail_succesfull(self):
        """Test create user with email succesfully"""
        email = 'hillergon@gmail.com'
        password = 'adminkangogo'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))



    def test_normalize_user_email(self):
        """test email for new user is nomalized"""
        email = 'kangogo@BARATEL.com'
        user = get_user_model().objects.create_user(email, 'barazel')
        self.assertEqual(user.email, email.lower())

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

    def test_tag_str(self):
        """test the tag str representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='nyama'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredients_str(self):
        """test ingrediens str representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Onion'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recpe_str(self):
        """test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='ugali',
            time_minutes=10,
            price=20.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

