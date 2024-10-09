# type: ignore

import unittest
from dataclasses import dataclass, field
from typing import List
from birchrest.routes.validator import parse_data_class

@dataclass
class SimpleDataClass:
    name: str
    age: int = field(metadata={"min_value": 18})


@dataclass
class DataClassWithDefaults:
    name: str = "Default Name"
    age: int = 25


@dataclass
class DataClassWithList:
    items: List[int] = field(default_factory=list)


@dataclass
class NestedDataClass:
    simple: SimpleDataClass
    is_active: bool

@dataclass
class RegexDataClass:
    email: str = field(metadata={"regex": r"[^@]+@[^@]+\.[^@]+"})
    phone: str = field(metadata={"regex": r"^\d{10}$"})
    postal_code: str = field(metadata={"regex": r"^\d{5}$"})



class TestParseDataClass(unittest.TestCase):
    
    def test_parse_simple_data_class(self):
        data = {"name": "John", "age": 30}
        parsed = parse_data_class(SimpleDataClass, data)
        self.assertEqual(parsed.name, "John")
        self.assertEqual(parsed.age, 30)
    
    def test_parse_data_class_with_defaults(self):
        data = {"name": "Alice"}
        parsed = parse_data_class(DataClassWithDefaults, data)
        self.assertEqual(parsed.name, "Alice")
        self.assertEqual(parsed.age, 25)

    def test_parse_data_class_with_missing_required_field(self):
        data = {"name": "John"}
        with self.assertRaises(ValueError) as context:
            parse_data_class(SimpleDataClass, data)
        self.assertIn("Missing required field: age", str(context.exception))

    def test_parse_data_class_with_invalid_integer(self):
        data = {"name": "John", "age": "abc"}
        with self.assertRaises(ValueError) as context:
            parse_data_class(SimpleDataClass, data)
        self.assertIn("Field 'age' must be a valid integer", str(context.exception))
    
    def test_parse_data_class_with_list(self):
        data = {"items": [1, 2, 3]}
        parsed = parse_data_class(DataClassWithList, data)
        self.assertEqual(parsed.items, [1, 2, 3])

    def test_parse_data_class_with_invalid_list_item_type(self):
        data = {"items": [1, "two", 3]}
        with self.assertRaises(ValueError) as context:
            parse_data_class(DataClassWithList, data)
        self.assertIn("All items in field 'items' must be of type <class 'int'>", str(context.exception))

    def test_parse_nested_data_class(self):
        data = {"simple": {"name": "John", "age": 30}, "is_active": True}
        parsed = parse_data_class(NestedDataClass, data)
        self.assertEqual(parsed.simple.name, "John")
        self.assertEqual(parsed.simple.age, 30)
        self.assertEqual(parsed.is_active, True)

    
    def test_parse_nested_data_class_missing_required_field(self):
        data = {"simple": {"name": "John"}, "is_active": True}
        with self.assertRaises(ValueError) as context:
            parse_data_class(NestedDataClass, data)
        self.assertIn("Missing required field: age", str(context.exception))

    def test_parse_data_class_with_integer_as_string(self):
        data = {"name": "John", "age": "30"}
        parsed = parse_data_class(SimpleDataClass, data)
        self.assertEqual(parsed.age, 30)

    def test_parse_data_class_with_invalid_min_value(self):
        data = {"name": "John", "age": 15}
        with self.assertRaises(ValueError) as context:
            parse_data_class(SimpleDataClass, data)
        self.assertIn("Field 'age' must be at least", str(context.exception))
    
    def test_parse_data_class_with_valid_regex(self):
        data = {
            "email": "test@example.com",
            "phone": "1234567890",
            "postal_code": "12345"
        }
        result = parse_data_class(RegexDataClass, data)
        self.assertEqual(result.email, "test@example.com")
        self.assertEqual(result.phone, "1234567890")
        self.assertEqual(result.postal_code, "12345")

    def test_parse_data_class_with_invalid_email(self):
        data = {
            "email": "invalid-email",
            "phone": "1234567890",
            "postal_code": "12345"
        }
        with self.assertRaises(ValueError) as context:
            parse_data_class(RegexDataClass, data)
        self.assertIn("Field 'email' was malformed", str(context.exception))

    def test_parse_data_class_with_invalid_phone(self):
        data = {
            "email": "test@example.com",
            "phone": "12345",
            "postal_code": "12345"
        }
        with self.assertRaises(ValueError) as context:
            parse_data_class(RegexDataClass, data)
        self.assertIn("Field 'phone' was malformed", str(context.exception))

    def test_parse_data_class_with_invalid_postal_code(self):
        data = {
            "email": "test@example.com",
            "phone": "1234567890",
            "postal_code": "abcde"
        }
        with self.assertRaises(ValueError) as context:
            parse_data_class(RegexDataClass, data)
        self.assertIn("Field 'postal_code' was malformed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
