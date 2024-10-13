# type: ignore

import unittest
from unittest.mock import Mock
from birchrest.decorators import (
    get,
    post,
    put,
    patch,
    delete,
    head,
    options,
    body,
    controller,
    middleware,
    params,
    protected,
    queries,
)


class TestDecorators(unittest.TestCase):

    def test_get_decorator(self):
        """Test the GET decorator."""

        @get("get_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "GET")
        self.assertEqual(getattr(sample_function, "_sub_route"), "get_route")

    def test_post_decorator(self):
        """Test the POST decorator."""

        @post("post_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "POST")
        self.assertEqual(getattr(sample_function, "_sub_route"), "post_route")

    def test_put_decorator(self):
        """Test the PUT decorator."""

        @put("put_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "PUT")
        self.assertEqual(getattr(sample_function, "_sub_route"), "put_route")

    def test_patch_decorator(self):
        """Test the PATCH decorator."""

        @patch("patch_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "PATCH")
        self.assertEqual(getattr(sample_function, "_sub_route"), "patch_route")

    def test_delete_decorator(self):
        """Test the DELETE decorator."""

        @delete("delete_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "DELETE")
        self.assertEqual(getattr(sample_function, "_sub_route"), "delete_route")

    def test_head_decorator(self):
        """Test the HEAD decorator."""

        @head("head_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "HEAD")
        self.assertEqual(getattr(sample_function, "_sub_route"), "head_route")

    def test_options_decorator(self):
        """Test the OPTIONS decorator."""

        @options("options_route")
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_http_method"), "OPTIONS")
        self.assertEqual(getattr(sample_function, "_sub_route"), "options_route")

    def test_decorator_with_empty_sub_route(self):
        """Test that decorators work with empty sub-routes."""

        @get()
        def get_function():
            pass

        @post()
        def post_function():
            pass

        self.assertEqual(getattr(get_function, "_sub_route"), "")
        self.assertEqual(getattr(post_function, "_sub_route"), "")

    def test_body_decorator(self):
        """Test the body decorator."""
        model_mock = Mock()

        @body(model_mock)
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_validate_body"), model_mock)

    def test_controller_decorator(self):
        """Test the controller decorator."""

        @controller("/api/v1")
        class SampleController:
            pass

        self.assertEqual(getattr(SampleController, "_base_path"), "/api/v1")

    def test_middleware_decorator_on_function(self):
        """Test the middleware decorator on a function."""
        middleware_mock = Mock()

        @middleware(middleware_mock)
        def sample_function():
            pass

        self.assertIn(middleware_mock, getattr(sample_function, "_middlewares"))

    def test_middleware_decorator_on_class(self):
        """Test the middleware decorator on a class."""
        middleware_mock = Mock()

        @middleware(middleware_mock)
        class SampleController:
            pass

        self.assertIn(middleware_mock, getattr(SampleController, "_middlewares"))

    def test_params_decorator(self):
        """Test the params decorator."""
        model_mock = Mock()

        @params(model_mock)
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_validate_params"), model_mock)

    def test_protected_decorator(self):
        """Test the protected decorator."""

        @protected()
        def sample_function():
            pass

        self.assertTrue(getattr(sample_function, "_is_protected"))

    def test_queries_decorator(self):
        """Test the queries decorator."""
        model_mock = Mock()

        @queries(model_mock)
        def sample_function():
            pass

        self.assertEqual(getattr(sample_function, "_validate_queries"), model_mock)


if __name__ == "__main__":
    unittest.main()
