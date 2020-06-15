import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image',args=[recipe_id])


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

    def test_create_basic_recipe(self):
        """test creating basic recipe"""
        payload = {
            'title': 'ugali ya brown',
            'time_minutes': 25,
            'price': 70.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        # Loop through the above keys, get the vale and compare with what is stored in database
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """test create recipe with tags assigned"""
        tag1 = sample_tag(user=self.user, name='vegetarian')
        tag2 = sample_tag(user=self.user, name='matunda')
        payload = {
            'title': 'Githeri ya kenya',
            'tags': [tag1.id,tag2.id],
            'time_minutes': 40,
            'price': 99.00

        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        # retrieve all tags
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """test create recipes with ingredients assigned"""
        ingredient1 = sample_ingredient(user=self.user, name='onion')
        ingredient2 = sample_ingredient(user=self.user, name='cucumber')
        payload = {
            'title': 'kachumbari special',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 50,
            'price': 18.00
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # retrieve all ingredients
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_recipe_partial_update(self):
        """test update using patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='tumeric')

        payload = {
            'title': 'kuku kienyeji',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_recipe_full_update(self):
        """test updating recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Matumbo Boilo',
            'time_minutes': 38,
            'price': 123.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='kangogo@baratel.com',
            password='mypassword'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """removes all test files"""
        self.recipe.image.delete()

    # def test_upload_image_to_recipe(self):
    #     """test uploading image to recipe"""
    #     url = image_upload_url(self.recipe.id)
    #
    #     with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
    #         img = Image.new('RGB', (10, 10))
    #         img.save(ntf, format='JPEG')
    #         ntf.seek(0)
    #         res = self.client.post(url, {'image': ntf}, format='multipart')
    #     self.recipe.refresh_from_db()
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('image', res.data)
    #     self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """test upload invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,{'image':'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



