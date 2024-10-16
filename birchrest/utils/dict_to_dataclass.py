from dataclasses import make_dataclass
from typing import Any, Dict, List, Union


def dict_to_dataclass(base_name: str, data: Union[Dict[Any, Any], List[Any]]) -> Any:
    """
    Converts a dictionary (or list of dictionaries) into a dataclass with fields matching
    the dictionary keys and values. Handles nested dictionaries and lists of dictionaries
    by recursively creating dataclasses for them.

    Parameters:
        base_name (str): The base name for the generated dataclass.
        data (dict or list): The dictionary (or list of dictionaries) to convert into a dataclass.

    Returns:
        An instance of the generated dataclass populated with the dictionary (or list) data.
    """
    if isinstance(data, dict):
        unique_class_name = f"{base_name}_{id(data)}"

        fields = []
        values = {}
        for key, value in data.items():
            if isinstance(value, dict):
                nested_dataclass = dict_to_dataclass(f"{key}_nested", value)
                fields.append((key, type(nested_dataclass)))
                values[key] = nested_dataclass
            elif isinstance(value, list):
                fields.append((key, List[Any]))
                values[key] = [
                    (
                        dict_to_dataclass(f"{key}_list", item)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                fields.append((key, type(value)))
                values[key] = value

        dataclass = make_dataclass(unique_class_name, fields)
        return dataclass(**values)

    elif isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            dataclass_list = [dict_to_dataclass(base_name, item) for item in data]
            return dataclass_list

        return data
