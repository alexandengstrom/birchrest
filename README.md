# BirchRest

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/birchrest.svg)](https://pypi.org/project/birchrest/)
![Unit Tests](https://github.com/alexandengstrom/birchrest/actions/workflows/unit_test.yml/badge.svg)
[![Codecov](https://codecov.io/gh/alexandengstrom/birchrest/branch/main/graph/badge.svg)](https://codecov.io/gh/alexandengstrom/birchrest)
![Type Checking](https://github.com/alexandengstrom/birchrest/actions/workflows/type_checking.yml/badge.svg)
![Linting](https://github.com/alexandengstrom/birchrest/actions/workflows/linting.yml/badge.svg)


**BirchRest** is a simple, lightweight framework for setting up RESTful APIs with minimal configuration. It is designed to be intuitive and flexible, allowing developers to quickly create APIs without heavy dependencies.

## Table of contents

## Installation

## Quickstart

## Defining Controllers
In Birchrest, controllers are the building blocks of your API. Each controller defines multiple endpoints, and controllers can be nested to create hierarchical routes.
### Key Concepts
- **Base Path**: Each controller has a base path that defines where its routes are accessible. If a controller has subcontrollers, their base paths are combined, creating a nested structure.
- **Controller**: Setup: To create a controller:
    1. Inherit from the Controller class
    2. Use the @controller decorator on the class, passing the base path as an argument.
### Defining Endpoints
Inside a controller, use HTTP method decorators like @get or @post to define endpoints. These decorators can take an optional path to extend the controller’s base path for that specific route.
### Nesting Controllers
To nest controllers, define a constructor in your parent controller. Inside the constructor, use self.attach() to attach the subcontroller, and don’t forget to call the parent class constructor with super().

## Middleware
Middleware allows you to perform tasks before or after a request is processed by a controller, such as logging, modifying the request, or checking permissions. Birchrest provides built-in middleware for common tasks and the ability to define your own custom middleware.

### Custom Middlewares
You can create custom middleware to handle specific logic or modify request and response objects. This section explains how to define and register middleware in your application.

Middleware operates hierarchically, meaning it applies to all routes below the point where it’s defined. You can set up global middleware directly at the application level, or use decorators on controllers and routes. When applied to a controller, the middleware will affect all routes within that controller, as well as any nested controllers attached to it. If applied to a route it will be applied only on that route.

#### Requirements
A middleware must be callable and take three arguments. The Request object, Response object and NextFunction object.

```python
from birchrest import Request, Response, NextFunction

def my_middleware(req: Request, res: Response, next: NextFunction):
    if something:
        next()
    else:
        pass
        # By not calling next, we wont continue the callchain. 
```

If you want to keep a state in your middleware, it is recommended to create a class that implements the call method.

```python
from birchrest import Request, Response, NextFunction, ApiError

class MyMiddleware:
    def __init__(self, state: int):
        self.state = state

    def __call__(self, req: Request, res: Response, next: NextFunction):
        if self.state:
            next()
        else:
            raise ApiError.BAD_REQUEST()
```
### Built-in Middlewarea
Birchrest comes with several built-in middleware options that help manage common use cases, such as request logging, rate limiting or CORS support. These can be easily added to your API with minimal configuration.
## Data Validation
Data validation in Birchrest is supported via Python data classes. This allows for strict validation of request data (body, queries, and params) to ensure that all incoming data adheres to the expected structure

### Body Validation

### Query Validation

### URL Param Validation

## Authentication
Birchrest makes it easy to protect your API routes with authentication mechanisms. It allows you to define custom authentication handlers and easily mark routes as protected, ensuring that only authenticated requests are allowed access.
### Custom Auth Handlers
You can define your own authentication handler to manage how users are authenticated in your system. Once defined, Birchrest will handle the integration with the API.
### Protecting Routes
You can easily protect individual routes or entire controllers by marking them as requiring authentication. Birchrest will automatically handle unauthorized access by returning predefined error messages.

## Error Handling
By default, Birchrest will respond will standardized error messages with as good information as possible. For example, 404 when route doesnt exist or 400 if body validation fails. If any unhandled exceptions occurs in the controllers 500 will be returned.

### ApiError
The error handling is done via the class ApiError which have static methods to raise exceptions corresponding to HTTP status codes. For example, with this code:
```python
from birchrest import ApiError

raise ApiError.NOT_FOUND()
```
This will automatically be converted into a 404 response to the user.

An ApiError exception will have the attributes status_code and base_message which can be 404 and "Not Found" for example. It can also contain the attribute "user_message" if more specific info was given when the exception was raised. For example, if validation fails we will give the user information about why it failed.
### Custom Error Handler
If you want more control over the error handling, you can catch the exceptions by defining your own error handler. The handler must be callable and will receive a request, response and exception. If a custom error handler is defined it must handle the exception, otherwise 500 internal server error will always be returned to the user.

## Unit Testing
To simplify testing, the framework includes a test adapter class that simulates sending HTTP requests to your API. This allows you to test everything except the server itself, with all middlewares, authentication handlers, and other components functioning exactly as they would in a real request. The adapter returns the final response object, which you can inspect and assert in your tests.


