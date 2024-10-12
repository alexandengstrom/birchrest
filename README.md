# BirchRest

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/birchrest.svg)](https://pypi.org/project/birchrest/)
![Unit Tests](https://github.com/alexandengstrom/birchrest/actions/workflows/unit_test.yml/badge.svg)
![Type Checking](https://github.com/alexandengstrom/birchrest/actions/workflows/type_checking.yml/badge.svg)
![Linting](https://github.com/alexandengstrom/birchrest/actions/workflows/linting.yml/badge.svg)
[![codecov](https://codecov.io/gh/alexandengstrom/birchrest/branch/main/graph/badge.svg)](https://codecov.io/gh/alexandengstrom/birchrest)
[![Downloads](https://img.shields.io/pypi/dm/birchrest)](https://pypi.org/project/birchrest/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://alexandengstrom.github.io/birchrest/)
![GitHub last commit](https://img.shields.io/github/last-commit/alexandengstrom/birchrest)
![Repo Size](https://img.shields.io/github/repo-size/alexandengstrom/birchrest)

**BirchRest** is a simple, lightweight framework for setting up RESTful APIs with minimal configuration. It is designed to be intuitive and flexible.

Full documentation is available here:
https://alexandengstrom.github.io/birchrest

## Installation
You can install the latest version of birchrest using pip:
```python
pip install birchrest
```

## Table of Contents
1. [Introduction](#introduction)
2. [Defining Controllers](#defining-controllers)
   - [Key Concepts](#key-concepts)
   - [Defining Endpoints](#defining-endpoints)
   - [Nesting Controllers](#nesting-controllers)
3. [Middleware](#middleware)
   - [Custom Middlewares](#custom-middlewares)
   - [Built-in Middlewares](#built-in-middlewares)
4. [Data Validation](#data-validation)
   - [Query and URL Param Validation](#query-and-url-param-validation)
5. [Authentication](#authentication)
   - [Custom Auth Handlers](#custom-auth-handlers)
   - [Protecting Routes](#protecting-routes)
6. [Error Handling](#error-handling)
   - [ApiError](#apierror)
   - [Custom Error Handler](#custom-error-handler)
7. [Unit Testing](#unit-testing)


## Introduction
BirchRest is designed around a controller-based architecture. At runtime, the framework automatically constructs the API from your predefined controllers. For this to work, BirchRest needs access to all the controllers you define. This is achieved by creating a file named __birch__.py, which must import all the controllers you intend to use in your project.
```python
from birchrest import Controller
from birchrest.decorators import get, controller
from birchrest.http import Request, Response

@controller("api")
class MyController(Controller):

    @get("hello")
    async def hello(self, req: Request, res: Response):
        return res.send({"message": "Hello from the app!"})
```
To start the server, instantiate the BirchRest class and call its serve method.
```python
from birchrest import BirchRest

app = BirchRest()
app.serve()
```
## Defining Controllers
In Birchrest, controllers are the building blocks of your API. Each controller defines multiple endpoints, and controllers can be nested to create hierarchical routes.
### Key Concepts
- **Base Path**: Each controller has a base path that defines where its routes are accessible. If a controller has subcontrollers, their base paths are combined, creating a nested structure.

- **Controller Setup**: To create a controller:
    1. Inherit from the Controller class
    2. Use the @controller decorator on the class, passing the base path as an argument.
### Defining Endpoints
Inside a controller, use HTTP method decorators like @get or @post to define endpoints. These decorators can take an optional path to extend the controller’s base path for that specific route.

```python
# Create an endpoint that accepts PATCH method on route /myendpoint.
@patch("myendpoint")
async def patch(self, req: Request, res: Response):
    print(req.body)
    return res.send({"message": "success"})
```

You can use path variables by using colon in the path and then access them via the request object.
```python
@get("user/:id")
async def patch(self, req: Request, res: Response):
    userId = req.params.get("id")
    return res.send({"id": userId})
```

A route can also access queries in the same way:
```python
@get("user")
async def patch(self, req: Request, res: Response):
    name = req.queries.get("name")
    return res.send({"name": name})
```

It is possible to set automatic contraints for the body, queries and params via validation decorators. See section about validation.

### Nesting Controllers
To nest controllers, define a constructor in your parent controller. Inside the constructor, use self.attach() to attach the subcontroller, and don’t forget to call the parent class constructor with super().

```python
from birchrest import BirchRest, Controller
from birchrest.decorators import get, controller
from birchrest.http import Request, Response

@controller("resource")
class ResourceController(Controller):
    @get("hello")
    async def hello(self, req: Request, res: Response):
        return res.send({"message": "Hello from the app!"})

@controller("api")
class BaseController(Controller):
    def __init__(self):
        super().__init__()
        self.attach(ResourceController)
```
This will create the endpoint /api/resouce/hello

## Middleware
Middleware allows you to perform tasks before or after a request is processed by a controller, such as logging, modifying the request, or checking permissions. Birchrest provides built-in middleware for common tasks and the ability to define your own custom middleware.

### Custom Middlewares
You can create custom middleware to handle specific logic or modify request and response objects. This section explains how to define and register middleware in your application.

Middleware operates hierarchically, meaning it applies to all routes below the point where it’s defined. You can set up global middleware directly at the application level, or use decorators on controllers and routes. When applied to a controller, the middleware will affect all routes within that controller, as well as any nested controllers attached to it. If applied to a route it will be applied only on that route.

#### Requirements
A middleware should be a class that inherits from the Middleware class and it must implement an async call method. The call method will receive a Request, Response and NextFunction. If the NextFunction is called the call will continue to the next middleware or route handler. If not called, we wont continue. The next function must be awaited.

```python
from birchrest.http import Request, Response, Middleware
from birchrest.types import NextFunction
from birchrest.exceptions import ApiError

class MyMiddleware(Middleware):
    def __init__(self, state: int):
        self.state = state

    async def __call__(self, req: Request, res: Response, next: NextFunction):
        if self.state:
            await next()
        else:
            raise ApiError.BAD_REQUEST()
```

It is possible to execute things after next is called aswell, this means you can use middlewares for postprocessing aswell.
### Built-in Middlewares
Birchrest comes with several built-in middleware options that help manage common use cases, such as request logging, rate limiting or CORS support. These can be easily added to your API with minimal configuration. These can be imported from the middlewares module.

```python
from birchrest.middlewares import Cors, Logger, RateLimiter
```
## Data Validation
Data validation in Birchrest is supported via Python data classes. This allows for strict validation of request data (body, queries, and params) to ensure that all incoming data adheres to the expected structure.

To be able to use validation, you must also define the models. Example:
```python
@dataclass
class Address:
    street: str = field(metadata={"min_length": 3, "max_length": 100})
    city: str = field(metadata={"min_length": 2, "max_length": 50})

@dataclass
class User:
    username: str = field(metadata={"min_length": 3, "max_length": 20})
    email: str = field(metadata={"regex": r"^[\w\.-]+@[\w\.-]+\.\w+$"})
    age: int = field(metadata={"min_value": 0, "max_value": 120})
    address: Address
```

You can then use the @body, @queries and @params decorator with the dataclass as argument.

Example:
```python
@post("user")
@body(User)
async def create_user(self, req: Request, res: Response):
    # It is safe to pass the body directly since we have already validated it.
    save_to_database(request.body)
    return res.status(201).send()
```
If the validation fails, the user will get an automatic response. For example, if we try to post a user to the route above but passes a username with only two letters. We will receive this response:
```json
{
    "error": {
        "status": 400,
        "code": "Bad Request",
        "correlationId": "67ad2218-262e-478b-b767-04cfafd4315b",
        "message": "Body validation failed: Field 'username' must have at least 3 characters."
    }
}
```

Read more about how automatic error responses are handled in the error section.

### Query and URL Param Validation
Validating queries and params is done in the same way, just use the @queries and @params decorators instead.

## Authentication
Birchrest makes it easy to protect your API routes with authentication mechanisms. It allows you to define custom authentication handlers and easily mark routes as protected, ensuring that only authenticated requests are allowed access.
### Custom Auth Handlers
You can define your own authentication handler to manage how users are authenticated in your system. Once defined, Birchrest will handle the integration with the API. If your route handler returns a falsy value or raises an Exception, the execution will be stopped. Otherwise the return value from this function will be put under the user property in the request object. It is therefore possible to put information there that tells you which user sent a request.
### Protecting Routes
You can easily protect individual routes or entire controllers by marking them as requiring authentication. Birchrest will automatically handle unauthorized access by returning predefined error messages.

```python
from birchrest import BirchRest, Controller
from birchrest.decorators import get, controller
from birchrest.http import Request, Response

async def auth_handler(req: Request, res: Response):
    if req.headers.get("Authorization"):
        # Do your logic
        return { "id": 1 }
    
    return False

@controller("api")
class MyController(Controller):

    @protected()
    @get("protected")
    async def hello(self, req: Request, res: Response):
        return res.send({"message": "Hello from the app!"})

app = BirchRest()
app.register(MyController)
app.serve()

```

## Error Handling
By default, Birchrest will respond will standardized error messages with as good information as possible. For example, 404 when route doesnt exist or 400 if body validation fails. If any unhandled exceptions occurs in the controllers 500 will be returned.

### ApiError
The error handling is done via the class ApiError which have static methods to raise exceptions corresponding to HTTP status codes. For example, with this code:
```python
from birchrest.exceptions import ApiError

raise ApiError.NOT_FOUND()
```
This will automatically be converted into a 404 response to the user.

An ApiError exception will have the attributes status_code and base_message which can be 404 and "Not Found" for example. It can also contain the attribute "user_message" if more specific info was given when the exception was raised. For example, if validation fails we will give the user information about why it failed.
### Custom Error Handler
If you want more control over the error handling, you can catch the exceptions by defining your own error handler. The handler must be callable and will receive a request, response and exception. If a custom error handler is defined it must handle the exception, otherwise 500 internal server error will always be returned to the user.

## Unit Testing
To simplify testing, the framework includes a test adapter class that simulates sending HTTP requests to your API. This allows you to test everything except the server itself, with all middlewares, authentication handlers, and other components functioning exactly as they would in a real request. The adapter returns the final response object, which you can inspect and assert in your tests.


