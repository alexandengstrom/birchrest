"""
This module provides built-in middlewares for the BirchRest framework, as well as
the base class for creating custom user-defined middlewares.

Middlewares are used to process requests and responses, either globally or for 
specific routes. They are executed in the order they are registered and can perform 
tasks such as logging, handling CORS, rate-limiting, and more.

Built-in middlewares:
- **RateLimiter**: Limits the number of requests from a single client over a period of time.
- **Logger**: Logs incoming requests and outgoing responses, providing useful insights for debugging and monitoring.
- **Cors**: Handles Cross-Origin Resource Sharing (CORS) headers to manage access from different domains.

Custom middlewares:
- **Middleware**: This is the base class that users should inherit from to create their own middleware. 
  Custom middlewares should implement the `__call__` method to define their specific behavior. 
  Both synchronous and asynchronous middlewares are supported.

To use a middleware:
1. Built-in middlewares can be registered directly to a BirchRest application instance.
2. For custom middlewares, inherit from the `Middleware` class and implement the call method.

Example of a user-defined middleware:

```python
from birchrest.middleware import Middleware

class CustomMiddleware(Middleware):
    async def __call__(self, req, res, next):
        # Custom processing logic before handling the request
        print(f"Processing request {req.method} {req.path}")
        await next()  # Continue to the next middleware or route handler
        # Custom logic after handling the request
        print(f"Response sent with status {res.status_code}")

"""

from .rate_limiter import RateLimiter
from .logger import Logger
from .cors import Cors
from .middleware import Middleware

__all__ = ["RateLimiter", "Logger", "Cors", "Middleware"]
