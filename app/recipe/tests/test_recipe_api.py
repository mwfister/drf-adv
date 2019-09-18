from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Recipe
from recipe.serializers import RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_URL = reverse('recipe:recipe-list')


def create_sample_recipe(user, **params):
    """Quickly create a new recipe using provided params"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'cost': 3.50
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the recipe API for an authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'pass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list(self):
        """Test user can get a list of their recipes"""
        create_sample_recipe(user=self.user, title='Crab Soup', cost=500.50)
        create_sample_recipe(user=self.user, title='Souffle')
        recipes = Recipe.objects.all().order_by('-id')
        serialized = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized.data)
        self.assertSequenceEqual(res.data, serialized.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for only the user"""
        user2 = get_user_model().objects.create_user(
            'another@user.com',
            'pass234'
        )
        create_sample_recipe(user=user2)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serialized = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serialized.data)

    # def test_create_recipe_successful(self):
    #     """Test recipe creation with valid arguments is successful"""
    #     payload = {'title': "Crab Soup", 'cost': "5.50", 'time_minutes': 15}
    #     res = self.client.post('recipe post', payload)
    #
    #     recipe_exists = Recipe.objects.filter(title=payload['title']).exists(
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertTrue(recipe_exists)
