from dataclasses import is_dataclass
import textwrap
from typing import Dict, Any, List, Tuple
from .dataclass_to_model import dataclass_to_model
import re

from birchrest.routes import Route

import ast
import inspect
from birchrest.exceptions import ApiError
from birchrest.http import HttpStatus


from typing import Type

def extract_error_status_codes(func: Any) -> List[int]:
    """
    Extracts all the HTTP status codes from `ApiError` exceptions raised within the given function.

    :param func: The function to analyze.
    :return: A list of unique HTTP status codes found in the function.
    """
    
    source = inspect.getsource(func)
    source = textwrap.dedent(source)

    tree = ast.parse(source)

    status_codes = set()

    api_error_subclasses: Dict[str, Type[Any]] = {cls.__name__: cls for cls in ApiError.__subclasses__()}

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                error_name = node.exc.func.id
                if error_name in api_error_subclasses:
                    error_class = api_error_subclasses[error_name]
                    status_codes.add(error_class(user_message="").status_code)

    return list(status_codes)

def get_route_return_codes(route: Route) -> Dict[str, Any]:
    """
    Extracts all return codes for a given route, by analyzing the handler, middlewares, and auth handler.

    :param route: The Route object to analyze.
    :return: A dictionary containing the return codes and their descriptions.
    """
    status_codes = set()

    status_codes.update(extract_error_status_codes(route.func))

    for middleware in route.middlewares:
        status_codes.update(extract_error_status_codes(middleware))

    if route.auth_handler:
        status_codes.update(extract_error_status_codes(route.auth_handler))

    return_codes = {
        str(code): {
            "description": f"{HttpStatus.description(code)}",
        }
        for code in status_codes
    }

    return return_codes

def route_to_model(route: Route, models: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Converts a Route object into an OpenAPI-compliant model.

    :param route: The Route object to convert.
    :param models: Dictionary where models are stored, passed by reference.
    :return: A dictionary representing the OpenAPI path and method definition.
    """
    openapi_path = re.sub(r":(\w+)", r"{\1}", route.path)

    method = route.method.lower()
    
    handler_docstring = inspect.getdoc(route.func) or "No description provided"

    openapi_model: Dict[str, Any] = {
        method: {
            "summary": f"Operation for {route.method} {route.path}",
            "description": handler_docstring,
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        }
    }

    if route.validate_params:
        if is_dataclass(route.validate_params):
            param_model = dataclass_to_model(route.validate_params)

            for param_name, param_schema in param_model["properties"].items():
                openapi_model[method]["parameters"].append({
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": param_schema
                })


    if route.validate_queries:
        if is_dataclass(route.validate_queries):
            query_model = dataclass_to_model(route.validate_queries)

            for query_name, query_schema in query_model["properties"].items():
                openapi_model[method]["parameters"].append({
                    "name": query_name,
                    "in": "query",
                    "required": query_name in query_model["required"],
                    "schema": query_schema
                })



    if route.validate_body:
        if is_dataclass(route.validate_body):
            body_model = dataclass_to_model(route.validate_body)
            body_ref = f"#/components/schemas/{route.validate_body.__name__}"

            openapi_model[method]["requestBody"] = {
                "required": True, 
                "content": {
                    "application/json": {
                        "schema": {"$ref": body_ref}
                    }
                }
            }

            if route.validate_body.__name__ not in models:
                models[route.validate_body.__name__] = body_model

    return_codes = get_route_return_codes(route)
    openapi_model[method]["responses"].update(return_codes)

    return {openapi_path: openapi_model}


def merge_route_models(route_models: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges route models by their paths, combining different methods for the same path.

    :param route_models: List of individual route OpenAPI models.
    :return: A merged dictionary representing the combined OpenAPI paths.
    """
    merged_paths: Dict[str, Any] = {}

    for route_model in route_models:
        for path, methods in route_model.items():
            if path not in merged_paths:
                merged_paths[path] = {}
            merged_paths[path].update(methods)

    return merged_paths


def routes_to_openapi(routes: List[Route]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Converts a list of Route objects into an OpenAPI-compliant model.

    :param routes: List of Route objects to convert.
    :return: A dictionary representing the OpenAPI paths and methods definitions for all routes.
    """
    route_models = []
    models: Dict[str, Any] = {}
    
    for route in routes:
        route_model = route_to_model(route, models)
        route_models.append(route_model)

    merged_paths = merge_route_models(route_models)

    return merged_paths, models