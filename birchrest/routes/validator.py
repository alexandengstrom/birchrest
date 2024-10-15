from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Dict, Type, get_args, get_origin, Union
import re

from birchrest.exceptions import InvalidValidationModel


def parse_data_class(data_class: Type[Any], data: Any) -> Any:
    """
    Parses and validates data against a dataclass type, ensuring the data matches the
    field types, validation constraints (like min/max lengths, regex), and metadata
    such as default values. This function supports nested dataclasses and collections.

    The function checks if the provided data conforms to the field types and optional
    constraints specified in the dataclass. If the data is invalid, a ValueError
    is raised with a descriptive message.

    :param data_class: The dataclass type to validate against.
    :param data: The input data to be validated, typically a dictionary.
    :return: An instance of the dataclass with the validated data.
    :raises ValueError: If the data is missing required fields or if any validation fails.
    """

    if not (is_dataclass(data_class) and isinstance(data_class, type)):
        raise InvalidValidationModel(data_class)

    kwargs: Dict[str, Any] = {}
    for field in fields(data_class):
        field_name = field.name
        field_type = field.type
        field_metadata = field.metadata

        is_optional = field_metadata.get("is_optional", False)

        if field_name not in data:
            if is_optional:
                kwargs[field_name] = None
                continue
            if field.default is not MISSING:
                kwargs[field_name] = field.default
            elif field.default_factory is not MISSING:
                kwargs[field_name] = field.default_factory()
            else:
                raise ValueError(f"Missing required field: {field_name}")
        else:
            field_value: Any = data[field_name]

            origin_type = get_origin(field_type)

            # Handle Union types (Optional and others)
            if origin_type is Union:
                valid_types = get_args(field_type)
                valid_types = tuple(
                    t for t in valid_types if t is not type(None)
                )  # Remove NoneType

                if field_value is None and is_optional:
                    kwargs[field_name] = None
                    continue

                if not isinstance(field_value, valid_types):
                    valid_type_names = [
                        t.__name__ for t in valid_types if isinstance(t, type)
                    ]
                    raise ValueError(
                        f"Incorrect type for field '{field_name}', expected one of {valid_type_names}"
                    )

            # Handle basic types like int
            if field_type is int:
                try:
                    field_value = int(field_value)
                except ValueError as e:
                    raise ValueError(
                        f"Field '{field_name}' must be a valid integer."
                    ) from e

            # String validations (regex, min_length, max_length)
            if isinstance(field_value, str):
                min_length = field_metadata.get("min_length", None)
                max_length = field_metadata.get("max_length", None)
                regex = field_metadata.get("regex", None)

                if min_length is not None and len(field_value) < min_length:
                    raise ValueError(
                        f"Field '{field_name}' must have at least {min_length} characters."
                    )
                if max_length is not None and len(field_value) > max_length:
                    raise ValueError(
                        f"Field '{field_name}' must have at most {max_length} characters."
                    )
                if regex and not re.match(regex, field_value):
                    raise ValueError(f"Field '{field_name}' was malformed")

            # Handle numeric validations (min_value, max_value)
            if isinstance(field_value, (int, float)):
                min_value = field_metadata.get("min_value", None)
                max_value = field_metadata.get("max_value", None)

                if min_value is not None and field_value < min_value:
                    raise ValueError(
                        f"Field '{field_name}' must be at least {min_value}."
                    )
                if max_value is not None and field_value > max_value:
                    raise ValueError(
                        f"Field '{field_name}' must be at most {max_value}."
                    )

            # Handle lists and their constraints
            if origin_type is list:
                item_type = get_args(field_type)[0]

                min_items = field_metadata.get("min_items", None)
                max_items = field_metadata.get("max_items", None)
                unique = field_metadata.get("unique", False)

                if min_items is not None and len(field_value) < min_items:
                    raise ValueError(
                        f"Field '{field_name}' must have at least {min_items} items."
                    )
                if max_items is not None and len(field_value) > max_items:
                    raise ValueError(
                        f"Field '{field_name}' must have at most {max_items} items."
                    )
                if unique and len(field_value) != len(set(field_value)):
                    raise ValueError(f"Field '{field_name}' must have unique items.")

                for index, item in enumerate(field_value):
                    if isinstance(item, dict) and is_dataclass(item_type):
                        if isinstance(
                            item_type, type
                        ):  # Ensure that item_type is a dataclass type, not an instance
                            field_value[index] = parse_data_class(item_type, item)
                    elif not isinstance(item, item_type):
                        raise ValueError(
                            f"All items in field '{field_name}' must be of type {item_type}."
                        )

                kwargs[field_name] = field_value
                continue

            # Handle nested dataclasses
            if is_dataclass(field_type) and isinstance(field_value, dict):
                if isinstance(
                    field_type, type
                ):  # Ensure field_type is a dataclass type
                    kwargs[field_name] = parse_data_class(field_type, field_value)
            else:
                # General type validation
                if isinstance(field_type, type):
                    if not isinstance(field_value, field_type):
                        raise ValueError(
                            f"Incorrect type for field '{field_name}', expected {field_type.__name__}"
                        )

                kwargs[field_name] = field_value

    return data_class(**kwargs)
