from dataclasses import is_dataclass
import ast
import inspect
import textwrap
import re
from typing import Type
from typing import Dict, Any, List, Tuple
from .dataclass_to_model import dataclass_to_model
from birchrest.routes import Route
from birchrest.exceptions import ApiError
from birchrest.http import HttpStatus





def extract_status_codes(func: Any) -> Tuple[List[int], List[int]]:
    """
    Extracts all the HTTP status codes from `ApiError` exceptions raised within the given function.

    :param func: The function to analyze.
    :return: A list of unique HTTP status codes found in the function.
    """

    source = inspect.getsource(func)
    source = textwrap.dedent(source)

    tree = ast.parse(source)

    error_codes = set()
    success_codes = set()

    api_error_subclasses: Dict[str, Type[Any]] = {
        cls.__name__: cls for cls in ApiError.__subclasses__()
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                error_name = node.exc.func.id
                if error_name in api_error_subclasses:
                    error_class = api_error_subclasses[error_name]
                    error_codes.add(error_class(user_message="").status_code)

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "status" and isinstance(node.args[0], ast.Constant):
                success_code = node.args[0].value
                if isinstance(success_code, int):
                    if success_code > 299 or success_code < 200:
                        error_codes.add(success_code)
                    else:
                        success_codes.add(success_code)

    return list(success_codes), list(error_codes)


def get_route_return_codes(route: Route) -> Dict[str, Any]:
    """
    Extracts all return codes for a given route, by analyzing the handler, middlewares, and auth handler.

    :param route: The Route object to analyze.
    :return: A dictionary containing the return codes and their descriptions.
    """
    success_codes = set()
    error_codes = set()

    route_success_codes, route_error_codes = extract_status_codes(route.func)
    success_codes.update(route_success_codes)
    error_codes.update(route_error_codes)

    for middleware in route.middlewares:
        middleware_success_codes, middleware_error_codes = extract_status_codes(
            middleware
        )
        success_codes.update(middleware_success_codes)
        error_codes.update(middleware_error_codes)

    if route.auth_handler:
        auth_success_codes, auth_error_codes = extract_status_codes(route.auth_handler)
        success_codes.update(auth_success_codes)
        error_codes.update(auth_error_codes)

    return_codes = {}

    for code in success_codes:
        return_codes[str(code)] = {
            "description": f"{HttpStatus.description(code)}",
        }

    for code in error_codes:
        return_codes[str(code)] = {
            "description": f"{HttpStatus.description(code)}",
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
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }
            },
        }
    }

    if hasattr(route.func, "_openapi_tags"):
        openapi_model[method]["tags"] = getattr(route.func, "_openapi_tags")

    if route.validate_params:
        if is_dataclass(route.validate_params) and isinstance(
            route.validate_params, type
        ):
            param_model = dataclass_to_model(route.validate_params)

            for param_name, param_schema in param_model["properties"].items():
                openapi_model[method]["parameters"].append(
                    {
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": param_schema,
                    }
                )

    if route.validate_queries:
        if is_dataclass(route.validate_queries) and isinstance(
            route.validate_queries, type
        ):
            query_model = dataclass_to_model(route.validate_queries)

            for query_name, query_schema in query_model["properties"].items():
                openapi_model[method]["parameters"].append(
                    {
                        "name": query_name,
                        "in": "query",
                        "required": query_name in query_model["required"],
                        "schema": query_schema,
                    }
                )

    if route.validate_body:
        if is_dataclass(route.validate_body) and isinstance(route.validate_body, type):
            body_model = dataclass_to_model(route.validate_body)
            body_ref = f"#/components/schemas/{route.validate_body.__name__}"

            openapi_model[method]["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": body_ref}}},
            }

            if route.validate_body.__name__ not in models:
                models[route.validate_body.__name__] = body_model

    if hasattr(route, "produces") and route.produces:
        if is_dataclass(route.produces) and isinstance(route.produces, type):
            produces_model = dataclass_to_model(route.produces)
            produces_ref = f"#/components/schemas/{route.produces.__name__}"

            openapi_model[method]["responses"]["200"]["content"] = {
                "application/json": {"schema": {"$ref": produces_ref}}
            }

            if route.produces.__name__ not in models:
                models[route.produces.__name__] = produces_model

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
