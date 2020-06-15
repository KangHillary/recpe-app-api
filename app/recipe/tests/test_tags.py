from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializer import TagSerializer
from core.models import Tag, Recipe

# TAGS_URL = reverse('recipe:tags-list')
TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """test tags api that don't require auth"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to retrieve tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTests(TestCase):
    """test the authorized user tags api"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='hillary@baratel.com',
            password='password123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving tags"""

        Tag.objects.create(
            user=self.user,
            name='nyamas'
        )
        Tag.objects.create(
            user=self.user,
            name='mboga'
        )
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_tags_limited_to_user(self):
        """test tags are limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='other@baratel.com',
            password='mypasskangogo'
        )
        Tag.objects.create(
            user=user2,
            name='matumbo'
        )
        tag = Tag.objects.create(
            user=self.user,
            name='matoke'
        )

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)

    def test_create_tag_successful(self):
        """test create tag successfully"""
        payload = {'name': 'my test tag'}
        res = self.client.post(TAGS_URL, payload)
        tag_exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(tag_exists)

    def test_create_tag_invalid(self):
        """test creating fails with invalid payload"""
        payload = {'name':''}
        res = self.client.post(TAGS_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='breakoh')
        tag2 = Tag.objects.create(user=self.user, name='lunch')
        recipe = Recipe.objects.create(
            user = self.user,
            title = 'continenatl breakfast',
            time_minutes =23,
            price = 45.00
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_unique(self):
        """test that unique tags are retrieved by filtering by assigned"""

        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='lunch')
        recipe1 = Recipe.objects.create(
                user = self.user,
                title = 'continenatl breakfast',
                time_minutes =23,
                price = 45.00
            )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
                user = self.user,
                title = 'Mutura',
                time_minutes = 4,
                price = 13.00
            )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)

