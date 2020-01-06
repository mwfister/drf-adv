from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def get_recipe_detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, name='Main course'):
    """Quickly create and return a new tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Cinnamon'):
    """Quickly create and return a new ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = get_recipe_detail_url(recipe.id)
        res = self.client.get(url)

        serialized = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serialized.data)

    def test_create_recipe_successful(self):
        """Test recipe creation with valid arguments is successful"""
        payload = {'title': "Crab Soup", 'cost': 5.50, 'time_minutes': 15}
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Create a recipe with tags"""
        tag1 = create_sample_tag(user=self.user)
        tag2 = create_sample_tag(user=self.user, name='Salty')
        tag3 = create_sample_tag(user=self.user)

        payload = {
            'title': 'Food',
            'time_minutes': 4,
            'cost': 3.50,
            'tags': [
                tag1.id,
                tag2.id,
                tag3.id
            ]
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), len(payload['tags']))
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertIn(tag3, tags)
        self.assertSequenceEqual(res.data['tags'], payload['tags'])

    def test_create_recipe_with_ingredient(self):
        """Create a recipe with ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = create_sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Red Prawn Curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'cost': 8.99
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), len(payload['ingredients']))
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updaing a recipe with PATCH"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        new_tag = create_sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}
        url = get_recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), len(payload['tags']))
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))

        payload = {
            'title': 'Spaget',
            'time_minutes': 60,
            'cost': 20.00
        }
        url = get_recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.cost, payload['cost'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
