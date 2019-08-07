from app.calc import add, subtract
from django.test import TestCase


class CalcTests(TestCase):

    def test_add_numbers(self):
        """Test that two numbers are added"""
        self.assertEqual(add(3, 8), 11)

    def test_subtract_numbers(self):
        """Test provided inputs are subtracted"""
        self.assertEqual(subtract(5, 11), 6)
