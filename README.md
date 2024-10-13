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

## Quickstart
You can install the latest version of birchrest using pip:
```bash
pip install birchrest
```

Init a boilerplate project with birch init command:
```bash
birch init
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
BirchRest follows a controller-based architecture, where each controller represents a logical grouping of API routes. The framework automatically constructs your API at runtime from the controllers you define. To make this work, simply create a file named ```__birch__.py``` and import all your controllers into this file. BirchRest will use this file to discover and configure your API routes.
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

Or start the server via command line:
```bash
birch serve --port [PORT] --host [HOST] --log-level [LOG_LEVEL]
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

To define path variables, use a colon (```:```) in the path. You can then access these variables through the ```req.params``` object.
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

BirchRest is fully asynchronous, meaning all route handlers and middleware must be defined as async functions. This allows the framework to handle multiple requests concurrently without blocking. Ensure that all I/O-bound operations, such as database queries, file handling, or external API requests, are awaited properly. Failing to use async or forgetting to await asynchronous operations can lead to blocking behavior, defeating the purpose of using an asynchronous framework.

### Nesting Controllers
BirchRest supports hierarchical route structures by allowing controllers to inherit from other controllers. This creates nested routes where the child controller's base path is combined with the parent controller's base path. In BirchRest, subcontrollers are created by having one controller class inherit from another controller class.

This approach makes it easy to group related endpoints under a common path and manage them as a logical structure.

#### Example
Let’s say we have a base API controller and we want to nest a resource controller under it:
```python
from birchrest import Controller
from birchrest.decorators import get, controller
from birchrest.http import Request, Response

# Define the parent controller
@controller("api")
class BaseController(Controller):
    @get("status")
    async def status(self, req: Request, res: Response):
        return res.send({"message": "API is running"})

# Define the child controller that inherits from the parent
@controller("resource")
class ResourceController(BaseController):
    @get("hello")
    async def hello(self, req: Request, res: Response):
        return res.send({"message": "Hello from resource!"})

```
This will create the endpoint /api/resouce/hello.

In this example:

- The ```BaseController``` is the parent controller that handles routes under ```/api```.
- The ```ResourceController``` inherits from ```BaseController```, making it a child controller nested under ```/api/resource```.
- The route for the "hello" endpoint in ```ResourceController``` becomes ```/api/resource/hello```.
- The route for the "status" endpoint from ```BaseController``` is ```/api/status```.

By inheriting from BaseController, the ResourceController becomes a child, automatically inheriting and extending the parent’s routing structure.

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
from birchrest.exceptions import BadRequest

class MyMiddleware(Middleware):
    def __init__(self, state: int):
        self.state = state

    async def __call__(self, req: Request, res: Response, next: NextFunction):
        if self.state:
            await next()
        else:
            raise BadRequest
```

It is possible to execute things after next is called aswell, this means you can use middlewares for postprocessing aswell. Just like route handlers, all middleware in BirchRest must be asynchronous.
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
By default, BirchRest responds with standardized error messages and provides as much detail as possible when an error occurs. Common error responses like 404 (Not Found) when a route doesn't exist, or 400 (Bad Request) when body validation fails, are handled automatically. If an unhandled exception occurs within your controllers, a 500 Internal Server Error will be returned.

### ApiError
The **ApiError** class is the base class for a variety of HTTP exceptions such as NotFound, BadRequest, Unauthorized, and more. If any of these exceptions are raised during request handling, BirchRest will automatically convert them into the appropriate HTTP response with the correct status code and error message.
```python
from birchrest.exceptions import NotFound

raise NotFound
```
This will automatically generate a 404 Not Found HTTP response to the client, with the provided user-friendly message.

Each ApiError has the following attributes:

- ```status_code```: The HTTP status code (e.g., 404, 400, 500).
- ```base_message```: A default message associated with the status code (e.g., "Not Found" for 404).
- ```user_message```: An optional custom message that can provide more specific details about the error.

BirchRest supports the following common HTTP exceptions out-of-the-box:
- ```BadRequest``` (400)
- ```Unauthorized``` (401)
- ```Forbidden``` (403)
- ```NotFound``` (404)
- ```MethodNotAllowed``` (405)
- ```Conflict``` (409)
- ```UnprocessableEntity``` (422)
- ```InternalServerError``` (500)
- ```ServiceUnavailable``` (503)

- ```PaymentRequired``` (402)
- ```RequestTimeout``` (408)
- ```Gone``` (410)
- ```LengthRequired``` (411)
- ```PreconditionFailed``` (412)
- ```PayloadTooLarge``` (413)
- ```UnsupportedMediaType``` (415)
- ```TooManyRequests``` (429)
- ```UpgradeRequired``` (426)

The framework handles everything behind the scenes if any of these exceptions are raised. You don't need to manually craft the response or worry about setting the correct status code—BirchRest takes care of it.

### Custom Error Handler
If you need more control over how errors are handled, you can define your own custom error handler. This handler will receive the request, response, and exception as arguments. The handler must manage the exception explicitly; otherwise, a ```500 Internal Server Error``` will be returned by default.

## Unit Testing
To simplify testing, the framework includes a test adapter class that simulates sending HTTP requests to your API. This allows you to test everything except the server itself, with all middlewares, authentication handlers, and other components functioning exactly as they would in a real request. The adapter returns the final response object, which you can inspect and assert in your tests.

The TestAdapter class takes an instance of your app and then provides methods like get, post etc that accepts a path, headers and body.

```python
from birchrest import BirchRest
from birchrest.unittest import TestAdapter

app = BirchRest()
runner = TestAdapter(app)

response = runner.get("/your-route")
```

BirchRest also provides a custom TestCase class to make it easier to assert responses, example:

```python
import unittest

from birchrest import BirchRest
from birchrest.unittest import TestAdapter, BirchRestTestCase

class ApiTest(BirchRestTestCase):
    
    def setUp(self) -> None:
        app = BirchRest(log_level="test")
        self.runner = TestAdapter(app)
        
    async def test_user_route(self) -> None:
        response = await self.runner.get("/user")
        self.assertOk(response)
        
    async def test_invalid_id(self) -> None:
        response = await self.runner.get("/user/0")
        self.assertNotOk(response)
        self.assertStatus(response, 400)
        
        
if __name__ == "__main__":
    unittest.main()
```

## Request and Response Lifecycle in BirchRest
The BirchRest framework handles HTTP requests using a structured flow to ensure that all incoming requests are processed correctly, including middleware execution, validation, and error handling. This section explains the lifecycle of a request from when it is received by the server to when a response is sent back to the client.

#### 1. Receiving and Parsing the Request
When a client sends an HTTP request to the server, the server parses the raw request data into a Request object. This object encapsulates all details about the incoming request, such as headers, method (e.g., GET, POST), query parameters, URL parameters, and body data.
#### 2. Passing the Request to the App
Once the request object is created, it is passed to the main application (BirchRest) for handling. The app creates a new Response object, which will later be populated and returned to the client. The app then looks for a matching route by searching through all defined routes based on the request’s URL and HTTP method.
#### 3. Handling the Request in the App
The main request handling logic is performed by the handle_request method in the app. This method attempts to match the incoming request to a route and execute the following key steps:
- **Route Matching**: The app searches through all registered routes to find one that matches the URL path and HTTP method of the request. If a matching route is found, the request proceeds to that route. If no route matches, a 404 Not Found error is raised, or if the route exists but the HTTP method is incorrect, a 405 Method Not Allowed error is raised.
- **Passing the Request to the Route**: Once a route is matched, the app passes both the request and response objects to that route for further processing.
- **Error Handling**: If an exception occurs during request handling (such as an invalid request or missing route), the app catches the exception and attempts to generate an appropriate error response using predefined or custom error handlers.
#### 4. Route Execution
Each route in BirchRest is responsible for executing its logic and handling the request:
- **Middleware Execution**: When the request reaches the matched route, the route begins by executing any middleware associated with it. Middleware can modify the request or response objects, perform tasks such as logging or authentication, and decide whether to continue processing the request. Middleware runs in a chain, meaning each middleware can pass control to the next one, or halt the chain and send a response early.

   The route's __call__ method initiates this process by calling the first middleware in the stack. If no middleware interrupts the chain, the request proceeds to the route handler.
- **Authentication**: If the route is protected by authentication, the request must pass through an authentication handler. This handler validates the request (e.g., checking tokens or credentials). If authentication fails, a 401 Unauthorized error is raised, and the response is sent back to the client.
- **Validation**: If the route requires validation of the request body, query parameters, or URL parameters, the request data is checked against predefined data classes. If the data fails validation (e.g., missing required fields or incorrect types), a 400 Bad Request error is raised.
- **Executing the Route Handler**: Once middleware, authentication, and validation checks pass, the route handler function is executed. The route handler is responsible for performing the main business logic, such as fetching data, processing the request, or interacting with external services. After processing, the route handler populates the response object with the appropriate data and status code.
#### 5. Returning the Response
After the route handler completes, the response object (which was initially created at the beginning of the request) contains the data to be sent back to the client. This includes the HTTP status code, headers, and response body.

The final response is then returned to the server, which sends it to the client. If any errors occurred during the request lifecycle, they are automatically converted into error responses by the app’s error handler.
## Contributing
Contributions are welcome! Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file for details on how to get involved, submit pull requests, and report issues.

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


