# type: ignore

import unittest
from dataclasses import dataclass
from typing import Optional
from birchrest.openapi import route_to_model, routes_to_openapi
from birchrest.routes import Route
from birchrest.http import Request, Response


# Mock handler function
def mock_handler(req: Request, res: Response) -> None:
    pass


# Sample dataclasses to test with
@dataclass
class UserBodySchema:
    name: str
    age: int


@dataclass
class UserPathParamsSchema:
    id: str


@dataclass
class UserQuerySchema:
    search: Optional[str] = None
    limit: Optional[int] = None


class TestOpenApiGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_simple_route_to_model(self) -> None:
        """
        Test route_to_model for a route with body and path params.
        """
        route = Route(
            func=mock_handler,
            method="POST",
            path="/users/:id",
            middlewares=[],
            protected=False,
            validate_body=UserBodySchema,
            validate_queries=None,
            validate_params=UserPathParamsSchema,
        )

        expected_openapi_model = {
            "/users/{id}": {
                "post": {
                    "summary": "Operation for POST /users/:id",
                    "description": "No description provided",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserBodySchema"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }

        openapi_model = route_to_model(route)
        self.assertEqual(openapi_model, expected_openapi_model)

    def test_routes_to_openapi_with_multiple_routes(self) -> None:
        """
        Test routes_to_openapi for multiple routes, including path params and query params.
        """
        route_post = Route(
            func=mock_handler,
            method="POST",
            path="/users/:id",
            middlewares=[],
            protected=False,
            validate_body=UserBodySchema,
            validate_queries=None,
            validate_params=UserPathParamsSchema,
        )

        route_get = Route(
            func=mock_handler,
            method="GET",
            path="/users/:id",
            middlewares=[],
            protected=False,
            validate_body=None,
            validate_queries=UserQuerySchema,
            validate_params=UserPathParamsSchema,
        )

        paths, models = routes_to_openapi([route_post, route_get])

        expected_paths = {
            "/users/{id}": {
                "post": {
                    "summary": "Operation for POST /users/:id",
                    "description": "No description provided",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserBodySchema"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "get": {
                    "summary": "Operation for GET /users/:id",
                    "description": "No description provided",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }

        expected_models = {
            "UserBodySchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }

        self.assertEqual(paths, expected_paths)
        self.assertEqual(models, expected_models)


if __name__ == '__main__':
    unittest.main()
