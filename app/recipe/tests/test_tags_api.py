from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Tag
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_requirements(self):
        """Test that the login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user rags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(name="Vegan", user=self.user)
        Tag.objects.create(name="Carnivore", user=self.user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        other_user = get_user_model().objects.create_user(
            'other@user.com',
            'superSecretPassword'
        )
        Tag.objects.create(name="Vegan", user=self.user)
        Tag.objects.create(name="Carnivore", user=self.user)
        Tag.objects.create(name="Dessert", user=other_user)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(tags))
        self.assertEqual(res.data, serializer.data)
