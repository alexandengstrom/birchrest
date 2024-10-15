from typing import Any, Dict, Type, get_args, get_origin, Union
from dataclasses import fields, is_dataclass

def python_type_to_openapi(field_type: Any) -> Dict[str, Any]:
    """
    Maps a Python type to the corresponding OpenAPI type.
    """
    if field_type is int:
        return {"type": "integer"}
    elif field_type is float:
        return {"type": "number", "format": "float"}
    elif field_type is str:
        return {"type": "string"}
    elif field_type is bool:
        return {"type": "boolean"}
    return {"type": "object"}

def dataclass_to_model(dataclass: Type[Any]) -> Dict[str, Any]:
    """
    Converts a dataclass type to an OpenAPI model definition.
    
    :param dataclass: The dataclass type to convert.
    :return: A dictionary representing the OpenAPI model definition.
    """
    if not is_dataclass(dataclass):
        raise ValueError(f"{dataclass} is not a valid dataclass")

    model: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for field in fields(dataclass):
        field_type = field.type
        field_metadata = field.metadata

        origin_type = get_origin(field_type)
        if origin_type is Union:
            valid_types = get_args(field_type)
            field_type = valid_types[0]
            is_optional = True
        else:
            is_optional = False

        if get_origin(field_type) is list:
            item_type = get_args(field_type)[0]
            if is_dataclass(item_type) and isinstance(item_type, type):
                field_schema = {
                    "type": "array",
                    "items": dataclass_to_model(item_type)
                }
            else:
                field_schema = {
                    "type": "array",
                    "items": python_type_to_openapi(item_type)
                }

            if "min_items" in field_metadata:
                field_schema["minItems"] = field_metadata["min_items"]
            if "max_items" in field_metadata:
                field_schema["maxItems"] = field_metadata["max_items"]
            if "unique" in field_metadata:
                field_schema["uniqueItems"] = field_metadata["unique"]

            model["properties"][field.name] = field_schema

        elif is_dataclass(field_type) and isinstance(field_type, type):
            model["properties"][field.name] = dataclass_to_model(field_type)
        else:
            field_schema = python_type_to_openapi(field_type)

            if "min_length" in field_metadata:
                field_schema["minLength"] = field_metadata["min_length"]
            if "max_length" in field_metadata:
                field_schema["maxLength"] = field_metadata["max_length"]
            if "regex" in field_metadata:
                field_schema["pattern"] = field_metadata["regex"]
            if "min_value" in field_metadata:
                field_schema["minimum"] = field_metadata["min_value"]
            if "max_value" in field_metadata:
                field_schema["maximum"] = field_metadata["max_value"]

            model["properties"][field.name] = field_schema

        if not is_optional:
            model["required"].append(field.name)

    return model

