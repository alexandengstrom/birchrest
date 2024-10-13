# type: ignore

import unittest
from birchrest.unittest import BirchRestTestCase
from birchrest.http.response import Response


class TestBirchRestTestCase(BirchRestTestCase):
    """
    Unit tests to verify that the custom BirchRestTestCase assertions work correctly.
    """

    def test_assert_response_status_passes(self):
        """Test that assertResponseStatus passes with correct status code."""
        response = Response(correlation_id="test-corr-id")
        response.status(200).send({"message": "OK"})

        self.assertOk(response)
        self.assertStatus(response, 200)

    def test_assert_response_status_fails(self):
        """Test that assertResponseStatus fails with incorrect status code."""
        response = Response(correlation_id="test-corr-id")
        response.status(404).send({"message": "Not Found"})
        
        self.assertNotOk(response)

        with self.assertRaises(AssertionError):
            self.assertStatus(response, 200)

    def test_assert_response_header_passes(self):
        """Test that assertResponseHeader passes with correct header value."""
        response = Response(correlation_id="test-corr-id")
        response.set_header("X-Custom-Header", "TestValue")

        self.assertResponseHeader(response, "X-Custom-Header", "TestValue")

    def test_assert_response_header_fails(self):
        """Test that assertResponseHeader fails with incorrect header value."""
        response = Response(correlation_id="test-corr-id")
        response.set_header("X-Custom-Header", "WrongValue")

        with self.assertRaises(AssertionError):
            self.assertResponseHeader(response, "X-Custom-Header", "TestValue")


if __name__ == '__main__':
    unittest.main()
