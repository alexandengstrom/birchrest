"""
This module provides routing and validation components for the BirchRest framework.

Components:
- **Controller**: A base class for defining groups of routes, organizing request handling logic.
- **Route**: Represents an individual route, mapping HTTP methods and paths to handler functions.
- **parse_data_class**: A utility function for validating and parsing request data using dataclasses.

Exported components:
- `Controller`
- `Route`
- `parse_data_class`
"""

from .controller import Controller
from .route import Route
from .validator import parse_data_class

__all__ = ["Controller", "Route", "parse_data_class"]
