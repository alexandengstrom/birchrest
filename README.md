# BirchRest

[![PyPI version](https://badge.fury.io/py/birchrest.svg)](https://pypi.org/project/birchrest/)
![GitHub Release Date](https://img.shields.io/github/release-date/alexandengstrom/birchrest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![GitHub issues](https://img.shields.io/github/issues/alexandengstrom/birchrest)
![GitHub last commit](https://img.shields.io/github/last-commit/alexandengstrom/birchrest)
![Unit Tests](https://github.com/alexandengstrom/birchrest/actions/workflows/unit_test.yml/badge.svg)
![Type Checking](https://github.com/alexandengstrom/birchrest/actions/workflows/type_checking.yml/badge.svg)
![Linting](https://github.com/alexandengstrom/birchrest/actions/workflows/linting.yml/badge.svg)
[![codecov](https://codecov.io/gh/alexandengstrom/birchrest/branch/main/graph/badge.svg)](https://codecov.io/gh/alexandengstrom/birchrest)
[![Downloads](https://img.shields.io/pypi/dm/birchrest)](https://pypi.org/project/birchrest/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://alexandengstrom.github.io/birchrest/)
![Repo Size](https://img.shields.io/github/repo-size/alexandengstrom/birchrest)

**BirchRest** is a simple, lightweight framework for setting up RESTful APIs with minimal configuration. It is designed to be intuitive and flexible.

Full documentation is available here:
https://alexandengstrom.github.io/birchrest

## Quickstart
1. **Install**: You can install the latest version of birchrest     using pip:
    ```bash
    pip install birchrest
    ```

2. **Init**: Create a boilerplate project with ```birch init``` command:
    ```bash
    birch init
    ```

3. **Start**: Start the server via command line:
    ```bash
    birch serve
    ```

## Table of Contents
## Table of Contents
1. [Introduction](#introduction)
2. [Defining Controllers](#defining-controllers)
    - [Key Concepts](#key-concepts)
    - [Defining Endpoints](#defining-endpoints)
    - [Nesting Controllers](#nesting-controllers)
3. [Middleware](#middleware)
    - [Custom Middlewares](#custom-middlewares)
        - [Requirements](#requirements)
    - [Built-in Middlewares](#built-in-middlewares)
        - [Rate Limiter](#rate-limiter)
        - [Cors](#cors)
4. [Data Validation](#data-validation)
    - [Body Validation](#body-validation)
    - [Query and URL Param Validation](#query-and-url-param-validation)
    - [Supported Validation Constraints](#supported-validation-constraints)
        - [Type Validation](#type-validation)
        - [String Constraints](#string-constraints)
        - [Numeric Constraints](#numeric-constraints)
        - [Optional Fields](#optional-fields)
        - [List Constraints](#list-constraints)
        - [Nested Dataclasses](#nested-dataclasses)
5. [Authentication](#authentication)
    - [Custom Auth Handlers](#custom-auth-handlers)
    - [Protecting Routes](#protecting-routes)
6. [Error Handling](#error-handling)
    - [ApiError](#apierror)
    - [Custom Error Handler](#custom-error-handler)
7. [Unit Testing](#unit-testing)
    - [Test Adapter](#test-adapter)
    - [BirchRestTestCase](#birchresttestcase)
8. [Requests And Responses](#requests-and-responses)
    - [Request](#request)
    - [Response](#response)
    - [Request and Response Lifecycle](#request-and-response-lifecycle)
        - [1. Receiving and Parsing the Request](#1-receiving-and-parsing-the-request)
        - [2. Passing the Request to the App](#2-passing-the-request-to-the-app)
        - [3. Handling the Request in the App](#3-handling-the-request-in-the-app)
        - [4. Route Execution](#4-route-execution)
        - [5. Returning the Response](#5-returning-the-response)
9. [OpenAPI](#openapi)
    - [How It Works](#how-it-works-2)
    - [Automatic Response Code Detection](#automatic-response-code-detection)
    - [Customizing](#customizing-openapi-information)
    - [Generating](#generating-the-openapi-spec)
10. [Contributing](#contributing)
11. [License](#license)


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
#### Rate Limiter
The RateLimiter middleware in BirchRest helps protect your API from abuse by limiting the number of requests a client (identified by their IP address or token) can make within a specified time window. It is particularly useful for preventing denial-of-service (DoS) attacks or enforcing fair usage limits.

##### How it works:
- The rate limiter tracks the number of requests made by each client within a rolling time window.
- If a client exceeds the allowed number of requests within the window, the middleware responds with a ```429 Too Many Requests``` error.
- Requests older than the current time window are automatically cleared from the log to allow new requests.
##### Configuration Options:
- ```max_requests```: The maximum number of requests a client can make within the time window (default is 2).
- ```window_seconds```: The length of the time window in seconds during which the requests are counted (default is 10 seconds).
##### Example:
```python
from birchrest.middlewares import RateLimiter

# Apply rate limiting globally
app.middleware(RateLimiter(max_requests=5, window_seconds=60))
```
In this example, the middleware limits each client to a maximum of 5 requests per 60 seconds. If the limit is exceeded, any additional requests within that time will receive a ```429``` error response.
#### Cors
The CORS (```Cross-Origin Resource Sharing```) middleware in BirchRest enables your API to respond to cross-origin requests securely by controlling which origins, methods, and headers are allowed. It also handles preflight (```OPTIONS```) requests for methods other than ```GET``` and ```POST```, or when using custom headers.
##### How It Works:
- The middleware inspects each request and adds the necessary CORS headers to the response based on the configured settings. This allows browsers to enforce the CORS policy and determine if the request is permitted.
- For preflight requests (```OPTIONS``` method), it sends the appropriate response headers to indicate which origins, methods, and headers are allowed.
- For regular requests, it ensures the appropriate headers are added to allow cross-origin resource sharing.
##### Configuration Options:
- ```allow_origins```: List of allowed origins (default is ["*"], allowing all origins).
- ```allow_methods```: List of allowed HTTP methods (default includes GET, POST, PUT, DELETE, PATCH, OPTIONS).
- ```allow_headers```: List of allowed request headers (default is ["Content-Type", "Authorization"]).
- ```allow_credentials```: Whether credentials (cookies, HTTP authentication, etc.) are allowed (default is False).
- ```max_age```: The time (in seconds) that preflight request results can be cached by the browser (default is 86400 seconds or 24 hours).
##### Example:
```python
from birchrest.middlewares import Cors

# Apply CORS middleware globally with default settings
app.middleware(Cors(allow_origins=["https://example.com"], allow_credentials=True))
```
In this example, only requests from https://example.com are allowed, and credentials (like cookies) are permitted to be sent with cross-origin requests. The middleware ensures that the appropriate CORS headers are added to all responses.
## Data Validation
Data validation in Birchrest is supported via Python data classes. This allows for strict validation of request data (body, queries, and params) to ensure that all incoming data adheres to the expected structure.

To be able to use validation, you must also define the models. 
### Body Validation
#### Example:
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

### Supported Validation Constraints
Below is a list of all the validation constraints you can define using ```field(metadata={...})```:
1. #### Type Validation: 
    Data is automatically validated against the field's type. Supported types include int, float, str, list, and nested dataclasses.
    Example:

    ```python
    @dataclass
    class User:
        age: int
    ```
2. #### String Constraints:

    - ```min_length```: Ensures that the string has at least a certain number of characters.
    - ```max_length```: Ensures that the string does not exceed a certain number of characters.
    - ```regex```: Ensures that the string matches a given regular expression.
    - Example:
    ```python
    @dataclass
    class User:
        username: str = field(metadata={"min_length": 3, "max_length": 20})
        email: str = field(metadata={"regex": r"[^@]+@[^@]+\.[^@]+"})

    ```
3. #### Numeric Constraints:
    - ```min_value```: Ensures that the number is at least a certain value.
    - ```max_value```: Ensures that the number does not exceed a certain value.
    - ```Example```:
    ```python
    @dataclass
    class User:
        age: int = field(metadata={"min_value": 18, "max_value": 120})

    ```
4. #### Optional Fields:
    - Fields can be marked as optional by specifying ```is_optional: True``` in the metadata. This allows a field to be omitted from the input data without causing a validation error.
    - Example:
    ```python
    @dataclass
    class User:
        age: Optional[int] = field(metadata={"is_optional": True})
        phone: Optional[str] = field(metadata={"is_optional": True, "regex": r"^\d{10}$"})

    ```
5. #### List Constraints:
    - ```min_items```: Ensures that a list has at least a certain number of items.
    - ```max_items```: Ensures that a list does not exceed a certain number of items.
    - ```unique```: Ensures that all items in the list are unique.
    - You can also nest dataclasses inside lists and apply validation to each item.
    - Example:
    ```python
    @dataclass
    class Address:
        street: str = field(metadata={"min_length": 5, "max_length": 100})

    @dataclass
    class User:
        addresses: List[Address] = field(metadata={"min_items": 1, "max_items": 3})

    ```
6. #### Nested Dataclasses:
    - You can nest dataclasses inside each other, and BirchRest will automatically validate nested structures.
    - Example:
    ```python
    @dataclass
    class ContactInfo:
        email: str = field(metadata={"regex": r"[^@]+@[^@]+\.[^@]+"})

    @dataclass
    class User:
        username: str = field(metadata={"min_length": 3, "max_length": 20})
        contact_info: ContactInfo
    ```
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

#### Example:
```python
from birchrest.http import Request, Response
from birchrest.exceptions import ApiError

async def error_handler(req: Request, res: Response, e: Exception) -> Response:
    if isinstance(e, ApiError):
        # If it an ApiError, use the build in converter if you want
        return e.convert_to_response(res)

    # Do your own error handling here...
    return res.status(500).send({"error": "This was not supposed to happen...."})
```
## Unit Testing
### Test Adapter
To simplify testing, the framework includes a test adapter class that simulates sending HTTP requests to your API. This allows you to test everything except the server itself, with all middlewares, authentication handlers, and other components functioning exactly as they would in a real request. The adapter returns the final response object, which you can inspect and assert in your tests.

The TestAdapter class takes an instance of your app and then provides methods like get, post etc that accepts a path, headers and body.

#### Example
```python
from birchrest import BirchRest
from birchrest.unittest import TestAdapter

app = BirchRest()
runner = TestAdapter(app)

response = runner.get("/your-route")
```

### BirchRestTestCase
BirchRest also provides a custom TestCase class (BirchRestTestCase) that includes helper methods to make it easier to assert HTTP responses. These methods help ensure that your API responds as expected. Below is a list of the available assertion methods and their descriptions:

- ```assertOk(response)```: Asserts that the response status code is in the range of 2xx, indicating a successful request.

- ```assertNotOk(response)```: Asserts that the response status code is not in the range of 2xx, indicating a failure.

- ```assertBadRequest(response)```: Asserts that the response status code is 400, indicating a Bad Request.

- ```assertNotFound(response)```: Asserts that the response status code is 404, indicating a resource was not found.

- ```assertUnauthorized(response)```: Asserts that the response status code is 401, indicating an Unauthorized request.

- ```assertForbidden(response)```: Asserts that the response status code is 403, indicating a Forbidden request.

- ```assertInternalServerError(response)```: Asserts that the response status code is 500, indicating an Internal Server Error.

- ```assertStatus(response, expected_status)```: Asserts that the response status code matches the expected_status.

- ```assertHasHeader(response, expected_key)```: Asserts that the response contains a specific header.

- ```assertHeader(response, header_name, expected_value)```: Asserts that a specific header in the response matches the expected value.

- ```assertRedirect(response, expected_url)```: Asserts that the response status is a redirect (3xx) and that the Location header matches the expected URL.

- ```assertBodyContains(response, expected_key)``: Asserts that the response body contains a specific property or key.

#### Example:
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

## Requests And Responses

### Request
The Request object represents the incoming HTTP request. It encapsulates all relevant information about the request, including the HTTP method, URL path, headers, body, query parameters, and more. The Request object provides access to these components, allowing you to handle and process the request effectively.
Properties:

- ```method: str```
    The HTTP method used for the request (e.g., GET, POST, PUT, DELETE).

- ```path: str```
    The full requested URL path, including any query string (e.g., /api/users?id=123).

- ```clean_path: str```
    The URL path without query parameters (e.g., /api/users).

- ```version: str```
    The HTTP version used for the request (e.g., HTTP/1.1).

- ```headers: Dict[str, str]```
    A dictionary of all HTTP request headers. Headers are case-insensitive.

    Example:

    ```python
    content_type = req.headers.get("content-type")
    ```

- ```queries: dataclass```
A dataclass of query parameters extracted from the URL. If a query parameter has multiple values, it will be a list. Otherwise, it will be a single string. If you have used the ```@queries``` decorator it will be your custom dataclass, otherwhise the request would have failed.

    Example:

    ```python
    search_query = req.queries.name
    ```

- ```params: dataclass```
A dataclass of URL path parameters (if any) extracted from the route. This is populated during route matching. You can also define this via the ```@params``` decorator.

    Example:

    ```python
    user_id = req.params.id
    ```

- ```body: dataclass```
The parsed body of the request. You can ensure this follows your exact dataclass model by using the ```@body``` decorator.

    Example:

    ```python
    user_data = req.body.user.name.firstName
    ```

- ```client_address: str```
The IP address of the client making the request.

- ```client_port: Optional[int]```
The port number used by the client to send the request. This is helpful for identifying the source of the request.

    Example:

    ```python
    print(f"Request received from {req.client_address}:{req.client_port}")
    ```

- ```correlation_id: str```
A unique ID automatically generated for each request. This can be used to track and correlate requests across different systems.

- ```received: datetime```
The timestamp indicating when the request was received by the server. This can be useful for logging and performance tracking.

    Example:

    ```python
    print(f"Request received at {req.received}")
    ```

- ```user: Optional[Any]```
Placeholder for any authenticated user information. This will be populated if the request goes through an authentication handler.

- ```host: Optional[str]```
The Host header from the request, which indicates the server's host (domain or IP) to which the request was made.

    Example:

    ```python
    print(f"Host: {req.host}")
    ```
- ```referrer: Optional[str]```
The Referer header (if present) from the request, which indicates the page from which the request originated.

- ```user_agent: Optional[str]```
The User-Agent header from the request, which identifies the client software (browser, bot, etc.).

### Response
The Response object in BirchRest is responsible for crafting the outgoing HTTP response that is sent back to the client. It provides methods to set the status code, headers, and body, with support for automatically sending JSON-encoded responses.

#### Important Methods

- ```status(code: int) -> Response```
    This method sets the HTTP status code for the response. You can either pass an integer representing the status code (e.g., 200 for OK or 404 for Not Found) or use the HttpStatus enum for predefined status codes. However, it is recommended to raise ```ApiError``` instead if you want to return errors. A good use would be when responding with 201. The status code is set to 200 by default, so if you intend to return that, you dont have to call status method.

    Example:
    ```python
    res.status(404)
    ```

- ```send(data: Any = {}) -> Response```
This method sets the response body by encoding the provided data as JSON and automatically sets the Content-Type header to application/json. The response can only be sent once; attempting to call send a second time will raise an exception.

    *Note: All responses in BirchRest are automatically sent as JSON.*

    Example:
    ```python
    res.status(200).send({"message": "Success"})  # Sends a JSON response with a 200 status code
    ```

    **Important:**
    - Once send is called, the response is finalized, and calling send again will result in an error ("Request was sent twice").
    - The Content-Length header is automatically set based on the length of the JSON-encoded response.
### Request and Response Lifecycle
The BirchRest framework handles HTTP requests using a structured flow to ensure that all incoming requests are processed correctly, including middleware execution, validation, and error handling. This section explains the lifecycle of a request from when it is received by the server to when a response is sent back to the client.

#### 1. Receiving and Parsing the Request
When a client sends an HTTP request to the server, the server parses the raw request data into a Request object. This object encapsulates all details about the incoming request, such as headers, method (e.g., GET, POST), query parameters, URL parameters, and body data.
#### 2. Passing the Request to the App
Once the request object is created, it is passed to the main application (BirchRest) for handling. The app creates a new Response object, which will later be populated and returned to the client. The app then looks for a matching route by searching through all defined routes based on the request’s URL and HTTP method.
#### 3. Handling the Request in the App
The main request handling logic is performed by the handle_request method in the app. This method attempts to match the incoming request to a route and execute the following key steps:
- **Route Matching**: The app searches through all registered routes to find one that matches the URL path and HTTP method of the request. If a matching route is found, the request proceeds to that route. If no route matches, a ```404 Not Found``` error is raised, or if the route exists but the HTTP method is incorrect, a ```405 Method Not Allowed``` error is raised.
- **Passing the Request to the Route**: Once a route is matched, the app passes both the request and response objects to that route for further processing.
- **Error Handling**: If an exception occurs during request handling (such as an invalid request or missing route), the app catches the exception and attempts to generate an appropriate error response using predefined or custom error handlers.
#### 4. Route Execution
Each route in BirchRest is responsible for executing its logic and handling the request:
- **Middleware Execution**: When the request reaches the matched route, the route begins by executing any middleware associated with it. Middleware can modify the request or response objects, perform tasks such as logging or authentication, and decide whether to continue processing the request. Middleware runs in a chain, meaning each middleware can pass control to the next one, or halt the chain and send a response early.

   The route's ```__call__``` method initiates this process by calling the first middleware in the stack. If no middleware interrupts the chain, the request proceeds to the route handler.
- **Authentication**: If the route is protected by authentication, the request must pass through an authentication handler. This handler validates the request (e.g., checking tokens or credentials). If authentication fails, a ```401 Unauthorized``` error is raised, and the response is sent back to the client.
- **Validation**: If the route requires validation of the request body, query parameters, or URL parameters, the request data is checked against predefined data classes. If the data fails validation (e.g., missing required fields or incorrect types), a 400 Bad Request error is raised.
- **Executing the Route Handler**: Once middleware, authentication, and validation checks pass, the route handler function is executed. The route handler is responsible for performing the main business logic, such as fetching data, processing the request, or interacting with external services. After processing, the route handler populates the response object with the appropriate data and status code.
#### 5. Returning the Response
After the route handler completes, the response object (which was initially created at the beginning of the request) contains the data to be sent back to the client. This includes the HTTP status code, headers, and response body.

The final response is then returned to the server, which sends it to the client. If any errors occurred during the request lifecycle, they are automatically converted into error responses by the app’s error handler.
## OpenAPI
One of the features of the framework is its ability to automatically generate OpenAPI specifications based on the defined routes, parameters, and decorators. This process integrates with the core functionality of the framework to ensure that your API documentation is always up-to-date without requiring manual intervention.

### How It Works

The framework reuses as much information as possible to define the structure of your API, which are then converted into OpenAPI schemas:

- **`@body`**, **`@queries`**, and **`@params`**: These decorators define the request body, query parameters, and path parameters respectively. The framework converts these into OpenAPI-compliant schemas, ensuring the input structure is well-documented.
  
- **`@produces`**: This decorator is used to specify the return type of a route, generating the corresponding schema for the response object. Note that while `@produces` defines the schema for the OpenAPI specification, it does not affect the runtime logic of the route itself.

- **`@tag`**: The `@tag` decorator allows you to attach tags to routes or controllers. These tags are used purely for documentation purposes in the OpenAPI spec, helping to categorize and organize your API endpoints.

- **`docstrings`**: The python docstrings for your route handlers will be reused to describe your endpoints.

### Automatic Response Code Detection

The framework analyzes the entire flow of a route to detect what HTTP status codes can be returned. By inspecting the **Abstract Syntax Tree (AST)** of the route handler, auth handler, middlewares, the framework can identify the status codes specified in the code, whether they are success or error codes. This process includes analyzing any exceptions (such as `ApiError`) raised within the route or its middlewares to ensure that all possible responses are captured.

### Customizing OpenAPI Information

In addition to automatically generating endpoint definitions, the framework allows you to specify additional metadata about your API. You can define information such as license, terms of service, and contact details by adding these fields to the `__birch__.py` file in your project. This information will be reflected in the OpenAPI specification's `info` section, making it easy to provide consumers with full details about your API.

### Generating the OpenAPI Spec

To generate the OpenAPI specification, simply run the following command:

```bash
birch openapi
```

It will create a file named openapi.json. It is possible to override the filename by providing the flag `--filename`.

```bash
birch openapi --filename myspec.json
```
## Contributing
Contributions are welcome! Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file for details on how to get involved, submit pull requests, and report issues.

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


