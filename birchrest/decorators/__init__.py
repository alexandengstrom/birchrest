"""
This module provides a collection of decorators for defining routes, controllers, 
middleware, and handling various aspects of HTTP requests in the BirchRest framework. 
These decorators simplify the process of routing, request validation, and protecting 
endpoints in the application.

Decorators:
- **HTTP method decorators**: Define routes for specific HTTP methods.
  - `@get`: Defines a route that handles HTTP GET requests.
  - `@post`: Defines a route that handles HTTP POST requests.
  - `@patch`: Defines a route that handles HTTP PATCH requests.
  - `@put`: Defines a route that handles HTTP PUT requests.
  - `@delete`: Defines a route that handles HTTP DELETE requests.
  - `@options`: Defines a route that handles HTTP OPTIONS requests.
  - `@head`: Defines a route that handles HTTP HEAD requests.

- **Controller decorator**:
  - `@controller`: Marks a class as a controller, where routes can be organized for better structure and reusability.

- **Middleware decorator**:
  - `@middleware`: Attaches middleware to specific routes or controllers for processing requests before they reach the handler.

- **Protected route decorator**:
  - `@protected`: Protects routes or controllers by enforcing authentication and authorization mechanisms.

- **Request body and query parameter decorators**:
  - `@body`: Validates and injects the body of the request into the handler.
  - `@queries`: Validates and injects query parameters from the URL into the handler.
  - `@params`: Validates and injects URL parameters into the handler.

Usage:
These decorators are used to define routes, middleware, and request-handling behavior in a declarative way. This enhances readability and modularity in the BirchRest framework by keeping routing and request-handling logic organized.

Example of usage:

```python
from birchrest.decorators import get, post, controller, middleware, protected, body

@controller("user")
class UserController:
    
    @get(":id")
    def get_users(self, req, res):
        # Handle GET request to /users
        res.send({"message": "List of users"})
    
    @post()
    def create_user(self, req, res):
        # Handle POST request to /users with middleware, body validation, and protection
        new_user = req.body  # User object automatically parsed
        res.status(201).send({"message": "User created", "user": new_user})
"""

from .get import get
from .post import post
from .controller import controller
from .middleware import middleware
from .protected import protected
from .body import body
from .queries import queries
from .params import params
from .put import put
from .patch import patch
from .delete import delete
from .options import options
from .head import head
from .produces import produces
from .tag import tag

__all__ = [
    "get",
    "post",
    "patch",
    "put",
    "delete",
    "options",
    "head",
    "controller",
    "middleware",
    "protected",
    "body",
    "queries",
    "params",
    "produces",
    "tag"
]
