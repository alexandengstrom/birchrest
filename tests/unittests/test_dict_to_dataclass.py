# type: ignore

import unittest
from typing import Any, List
from dataclasses import is_dataclass

from birchrest.utils import dict_to_dataclass


class TestDictToDataclass(unittest.TestCase):

    def test_normal_case(self):
        """Test a normal case where the dictionary has simple fields."""
        data = {
            'name': 'Alice',
            'age': 30,
            'is_student': False
        }

        result = dict_to_dataclass('Person', data)

        self.assertTrue(is_dataclass(result))
        self.assertEqual(result.name, 'Alice')
        self.assertEqual(result.age, 30)
        self.assertEqual(result.is_student, False)

    def test_empty_dict(self):
        """Test case where an empty dictionary is passed."""
        data = {}

        result = dict_to_dataclass('EmptyClass', data)

        self.assertTrue(is_dataclass(result))
        self.assertEqual(len(result.__dataclass_fields__), 0)

    def test_nested_dict(self):
        """Test a case with nested dictionaries."""
        data = {
            'name': 'Alice',
            'age': 30,
            'address': {
                'street': '123 Main St',
                'city': 'Wonderland'
            }
        }

        result = dict_to_dataclass('Person', data)

        self.assertTrue(is_dataclass(result))
        self.assertEqual(result.name, 'Alice')
        self.assertEqual(result.age, 30)

        self.assertTrue(is_dataclass(result.address))
        self.assertEqual(result.address.street, '123 Main St')
        self.assertEqual(result.address.city, 'Wonderland')

    def test_list_of_dicts(self):
        """Test a case with a list of dictionaries."""
        data = {
            'name': 'Alice',
            'courses': [
                {'title': 'Math', 'grade': 'A'},
                {'title': 'History', 'grade': 'B'}
            ]
        }

        result = dict_to_dataclass('Student', data)

        self.assertTrue(is_dataclass(result))
        self.assertIsInstance(result.courses, list)

        self.assertTrue(is_dataclass(result.courses[0]))
        self.assertEqual(result.courses[0].title, 'Math')
        self.assertEqual(result.courses[0].grade, 'A')

        self.assertTrue(is_dataclass(result.courses[1]))
        self.assertEqual(result.courses[1].title, 'History')
        self.assertEqual(result.courses[1].grade, 'B')

    def test_complex_nested_dicts_and_lists(self):
        """Test a complex case with deeply nested dictionaries and lists."""
        data = {
            'name': 'Alice',
            'address': {
                'street': '123 Main St',
                'city': 'Wonderland',
                'geo': {
                    'lat': 123.456,
                    'lng': 789.012
                }
            },
            'courses': [
                {'title': 'Math', 'grade': 'A'},
                {'title': 'History', 'grade': 'B'}
            ]
        }

        result = dict_to_dataclass('Person', data)

        self.assertTrue(is_dataclass(result))
        
        self.assertTrue(is_dataclass(result.address))
        self.assertEqual(result.address.street, '123 Main St')
        self.assertEqual(result.address.city, 'Wonderland')

        self.assertTrue(is_dataclass(result.address.geo))
        self.assertEqual(result.address.geo.lat, 123.456)
        self.assertEqual(result.address.geo.lng, 789.012)

        self.assertIsInstance(result.courses, list)
        self.assertTrue(is_dataclass(result.courses[0]))
        self.assertEqual(result.courses[0].title, 'Math')
        self.assertEqual(result.courses[0].grade, 'A')

    def test_list_of_primitives(self):
        """Test a list of primitives to make sure they are returned as-is."""
        data = {
            'name': 'Alice',
            'scores': [85, 90, 88]
        }

        result = dict_to_dataclass('Student', data)

        self.assertTrue(is_dataclass(result))
        self.assertIsInstance(result.scores, list)
        self.assertEqual(result.scores, [85, 90, 88])

    def test_mixed_list(self):
        """Test a list containing both dictionaries and primitives."""
        data = {
            'name': 'Alice',
            'mixed_list': [
                {'course': 'Math', 'grade': 'A'},
                42,
                {'course': 'History', 'grade': 'B'}
            ]
        }

        result = dict_to_dataclass('Student', data)

        self.assertTrue(is_dataclass(result))
        self.assertIsInstance(result.mixed_list, list)
        self.assertTrue(is_dataclass(result.mixed_list[0]))
        self.assertEqual(result.mixed_list[1], 42)
        self.assertTrue(is_dataclass(result.mixed_list[2]))


if __name__ == "__main__":
    unittest.main()
