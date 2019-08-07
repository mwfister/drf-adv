from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user w/ email is successful"""
        email = 'test@emailtest.com'
        password = 'pass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@TEStINPUt.cOM'
        user = get_user_model().objects.create_user(email, 'pass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'pass123')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@email.com',
            'pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
