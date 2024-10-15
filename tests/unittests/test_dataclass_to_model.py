import unittest
from dataclasses import dataclass, field
from typing import List, Optional
from birchrest.openapi import dataclass_to_model

@dataclass
class SimpleDataclass:
    name: str
    age: int

@dataclass
class OptionalDataclass:
    username: str
    email: Optional[str] = None

@dataclass
class ListDataclass:
    tags: List[str]
    ratings: List[int]

@dataclass
class NestedDataclass:
    user: SimpleDataclass
    active: bool
    
@dataclass
class ConstrainedStringDataclass:
    username: str = field(metadata={"min_length": 3, "max_length": 30, "regex": "^[a-zA-Z0-9_]+$"})

@dataclass
class ConstrainedNumberDataclass:
    age: int = field(metadata={"min_value": 18, "max_value": 99})
    height: Optional[float] = field(default=None, metadata={"min_value": 1.0, "max_value": 2.5})

@dataclass
class ConstrainedListDataclass:
    items: List[int] = field(metadata={"min_items": 2, "max_items": 5, "unique": True})

@dataclass
class NestedConstrainedDataclass:
    user: ConstrainedStringDataclass
    attributes: List[ConstrainedNumberDataclass]

class TestDataclassToModel(unittest.TestCase):
    
    def setUp(self) -> None:
        self.maxDiff = None 

    def test_simple_dataclass(self) -> None:
        """Test conversion of a simple dataclass."""
        expected_model = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"]
        }
        model = dataclass_to_model(SimpleDataclass)
        self.assertEqual(model, expected_model)

    def test_optional_field_dataclass(self) -> None:
        """Test conversion of a dataclass with an optional field."""
        expected_model = {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["username"]
        }
        model = dataclass_to_model(OptionalDataclass)
        self.assertEqual(model, expected_model)

    def test_list_field_dataclass(self) -> None:
        """Test conversion of a dataclass with list fields."""
        expected_model = {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "items": {"type": "string"}},
                "ratings": {"type": "array", "items": {"type": "integer"}}
            },
            "required": ["tags", "ratings"]
        }
        model = dataclass_to_model(ListDataclass)
        self.assertEqual(model, expected_model)

    def test_nested_dataclass(self) -> None:
        """Test conversion of a dataclass with a nested dataclass."""
        expected_model = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["name", "age"]
                },
                "active": {"type": "boolean"}
            },
            "required": ["user", "active"]
        }
        model = dataclass_to_model(NestedDataclass)
        self.assertEqual(model, expected_model)
        
    def test_constrained_string_dataclass(self) -> None:
        """Test conversion of a dataclass with string constraints (min_length, max_length, regex)."""
        expected_model = {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 30,
                    "pattern": "^[a-zA-Z0-9_]+$"
                },
            },
            "required": ["username"]
        }
        model = dataclass_to_model(ConstrainedStringDataclass)
        self.assertEqual(model, expected_model)

    def test_constrained_number_dataclass(self) -> None:
        """Test conversion of a dataclass with number constraints (min_value, max_value)."""
        expected_model = {
            "type": "object",
            "properties": {
                "age": {
                    "type": "integer",
                    "minimum": 18,
                    "maximum": 99,
                },
                "height": {
                    "type": "number",
                    "format": "float",
                    "minimum": 1.0,
                    "maximum": 2.5,
                }
            },
            "required": ["age"]
        }
        model = dataclass_to_model(ConstrainedNumberDataclass)
        self.assertEqual(model, expected_model)

    def test_constrained_list_dataclass(self) -> None:
        """Test conversion of a dataclass with list constraints (min_items, max_items, unique)."""
        expected_model = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 5,
                    "uniqueItems": True
                }
            },
            "required": ["items"]
        }
        model = dataclass_to_model(ConstrainedListDataclass)
        self.assertEqual(model, expected_model)

    def test_nested_constrained_dataclass(self) -> None:
        """Test conversion of a nested dataclass with constraints in both the parent and child."""
        expected_model = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "minLength": 3,
                            "maxLength": 30,
                            "pattern": "^[a-zA-Z0-9_]+$"
                        },
                    },
                    "required": ["username"]
                },
                "attributes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "age": {
                                "type": "integer",
                                "minimum": 18,
                                "maximum": 99
                            },
                            "height": {
                                "type": "number",
                                "format": "float",
                                "minimum": 1.0,
                                "maximum": 2.5
                            }
                        },
                        "required": ["age"]
                    }
                }
            },
            "required": ["user", "attributes"]
        }
        model = dataclass_to_model(NestedConstrainedDataclass)
        self.assertEqual(model, expected_model)

if __name__ == '__main__':
    unittest.main()
