from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ return recipe details url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user,name='main course'):
    """create and return sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user,name='tumeric'):
    """create and return sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """create and return a sample  recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 16,
        'price': 17.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test the unauthentiacated api requests"""
    def setup(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """test authentications is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code,
                         status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test unauthenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='kangogo@baratel.com',
                                                     password='mypassword')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """test only recipes belong to authenticated user"""

        user2 = get_user_model().objects.create_user('hillergon@bara.com',
                                                     'password34556')

        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_details(self):
        """test viewing recipe details"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        # Since this is detail, no use of many = true
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

