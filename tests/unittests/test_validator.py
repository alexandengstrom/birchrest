# type: ignore

import unittest
from dataclasses import dataclass, field
from typing import List, Optional
from birchrest.routes.validator import parse_data_class
from birchrest.exceptions import InvalidValidationModel

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

@dataclass
class OptionalFieldDataClass:
    name: str
    age: Optional[int] = field(metadata={"is_optional": True})
    phone: Optional[str] = field(metadata={"is_optional": True, "regex": r"^\d{10}$"})

@dataclass
class Address:
    street: str = field(metadata={"min_length": 5, "max_length": 100})
    city: str = field(metadata={"min_length": 2, "max_length": 50})
    postal_code: str = field(metadata={"regex": r"^\d{5}$"})


@dataclass
class ContactInfo:
    email: str = field(metadata={"regex": r"[^@]+@[^@]+\.[^@]+"})
    phone: Optional[str] = field(metadata={"is_optional": True, "regex": r"^\d{10}$"})


@dataclass
class UserProfile:
    username: str = field(metadata={"min_length": 3, "max_length": 20})
    age: int = field(metadata={"min_value": 18, "max_value": 120})
    contact_info: ContactInfo
    addresses: List[Address] = field(metadata={"min_items": 1, "max_items": 3})


@dataclass
class ComplexNestedDataClass:
    user_profile: UserProfile
    is_active: bool
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
    
    def test_parse_optional_field(self):
        """Test that optional fields are handled correctly."""
        data = {"name": "John"}
        parsed = parse_data_class(OptionalFieldDataClass, data)
        self.assertEqual(parsed.name, "John")
        self.assertIsNone(parsed.age)

    def test_parse_optional_field_with_value(self):
        """Test that optional fields are parsed correctly when provided."""
        data = {"name": "John", "age": 25}
        parsed = parse_data_class(OptionalFieldDataClass, data)
        self.assertEqual(parsed.age, 25)

    def test_parse_optional_field_with_invalid_value(self):
        """Test that optional fields validate correctly if provided."""
        data = {"name": "John", "phone": "1234"}
        with self.assertRaises(ValueError) as context:
            parse_data_class(OptionalFieldDataClass, data)
        self.assertIn("Field 'phone' was malformed", str(context.exception))

    def test_parse_optional_field_with_regex(self):
        """Test that optional fields with regex work when provided."""
        data = {"name": "John", "phone": "1234567890"}
        parsed = parse_data_class(OptionalFieldDataClass, data)
        self.assertEqual(parsed.phone, "1234567890")
        
    def test_parse_complex_nested_data_class(self):
        """Test parsing a complex nested dataclass with multiple constraints."""
        data = {
            "user_profile": {
                "username": "john_doe",
                "age": 30,
                "contact_info": {
                    "email": "john.doe@example.com",
                    "phone": "1234567890"
                },
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "Metropolis",
                        "postal_code": "12345"
                    },
                    {
                        "street": "456 Broadway",
                        "city": "Gotham",
                        "postal_code": "54321"
                    }
                ]
            },
            "is_active": True
        }

        parsed = parse_data_class(ComplexNestedDataClass, data)

        self.assertEqual(parsed.user_profile.username, "john_doe")
        self.assertEqual(parsed.user_profile.age, 30)
        self.assertEqual(parsed.user_profile.contact_info.email, "john.doe@example.com")
        self.assertEqual(parsed.user_profile.contact_info.phone, "1234567890")
        self.assertEqual(len(parsed.user_profile.addresses), 2)
        self.assertEqual(parsed.user_profile.addresses[0].street, "123 Main St")
        self.assertEqual(parsed.user_profile.addresses[1].city, "Gotham")
        self.assertTrue(parsed.is_active)

    def test_complex_data_class_invalid_age(self):
        """Test complex dataclass with invalid age."""
        data = {
            "user_profile": {
                "username": "john_doe",
                "age": 15,
                "contact_info": {
                    "email": "john.doe@example.com",
                    "phone": "1234567890"
                },
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "Metropolis",
                        "postal_code": "12345"
                    }
                ]
            },
            "is_active": True
        }

        with self.assertRaises(ValueError) as context:
            parse_data_class(ComplexNestedDataClass, data)
        self.assertIn("Field 'age' must be at least 18", str(context.exception))

    def test_complex_data_class_invalid_address(self):
        """Test complex dataclass with invalid postal code."""
        data = {
            "user_profile": {
                "username": "john_doe",
                "age": 30,
                "contact_info": {
                    "email": "john.doe@example.com",
                    "phone": "1234567890"
                },
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "Metropolis",
                        "postal_code": "abcde"
                    }
                ]
            },
            "is_active": True
        }

        with self.assertRaises(ValueError) as context:
            parse_data_class(ComplexNestedDataClass, data)
        self.assertIn("Field 'postal_code' was malformed", str(context.exception))

    def test_complex_data_class_too_many_addresses(self):
        """Test complex dataclass with too many addresses (violating max_items)."""
        data = {
            "user_profile": {
                "username": "john_doe",
                "age": 30,
                "contact_info": {
                    "email": "john.doe@example.com",
                    "phone": "1234567890"
                },
                "addresses": [
                    {"street": "123 Main St", "city": "Metropolis", "postal_code": "12345"},
                    {"street": "456 Broadway", "city": "Gotham", "postal_code": "54321"},
                    {"street": "789 Wall St", "city": "Star City", "postal_code": "67890"},
                    {"street": "101 Fifth Ave", "city": "Central City", "postal_code": "98765"}
                ]
            },
            "is_active": True
        }

        with self.assertRaises(ValueError) as context:
            parse_data_class(ComplexNestedDataClass, data)
        self.assertIn("Field 'addresses' must have at most 3 items", str(context.exception))

    def test_invalid_model(self):
        """Test that you cannot pass not dataclasses"""
        class NotDataclass:
            def __init__(self):
                self.name: str = "John Doe"

        data = {
            "name": "John Doe"
        }
        with self.assertRaises(InvalidValidationModel) as context:
            parse_data_class(NotDataclass, data)



if __name__ == '__main__':
    unittest.main()
