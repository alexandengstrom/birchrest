"""
This module provides the `TestAdapter`, a wrapper around the BirchRest app to simplify unit testing.

- **TestAdapter**: Facilitates testing by providing an easy way to simulate requests and inspect responses.

Exported components:
- `TestAdapter`
"""


from .test_adapter import TestAdapter
from .birchrest_test_case import BirchRestTestCase

__all__ = ["TestAdapter", "BirchRestTestCase"]
