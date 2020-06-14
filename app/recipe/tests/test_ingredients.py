from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializer import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsTests(TestCase):
    """test ingredients api that don't require authentication"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to access this endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTest(TestCase):
    """test requests that require auth"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='kangogo@baratel.com',
            password='passwordkangogo'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """test retrieveing a lust of ingredients"""
        Ingredient.objects.create(
            user = self.user,
            name = 'sugar'
        )
        Ingredient.objects.create(
            user=self.user,
            name='salt'
        )
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_ingredients_limited_to_user(self):
        """test only get ingredients for authent user"""
        user2 = get_user_model().objects.create_user(
            email='sergon@gmail.com',
            password='segonpasss'
        )
        Ingredient.objects.create(
            user=user2,
            name='sukuma wiki'
        )
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='kale'
        )

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)

    def test_create_ingredient_succesful(self):
        """test create new ingredient"""
        payload = {'name':'cabbage'}
        self.client.post(INGREDIENTS_URL,payload)
        ingredient_exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(ingredient_exists)

    def test_create_ingrendients_invalida(self):
        """test create invalid ingredient fail"""
        payload = {'name':''}
        res = self.client.post(INGREDIENTS_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)









