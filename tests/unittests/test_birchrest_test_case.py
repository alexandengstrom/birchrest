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

        self.assertHeader(response, "X-Custom-Header", "TestValue")

    def test_assert_response_header_fails(self):
        """Test that assertResponseHeader fails with incorrect header value."""
        response = Response(correlation_id="test-corr-id")
        response.set_header("X-Custom-Header", "WrongValue")

        with self.assertRaises(AssertionError):
            self.assertHeader(response, "X-Custom-Header", "TestValue")

    def test_assert_redirect_passes(self):
        """Test that assertRedirect passes with correct Location header."""
        response = Response(correlation_id="test-corr-id")
        response.status(302)
        response.set_header("Location", "https://example.com")

        self.assertRedirect(response, "https://example.com")

    def test_assert_redirect_fails(self):
        """Test that assertRedirect fails with incorrect Location header."""
        response = Response(correlation_id="test-corr-id")
        response.status(302)
        response.set_header("Location", "https://wrong-url.com")

        with self.assertRaises(AssertionError):
            self.assertRedirect(response, "https://example.com")

    def test_assert_body_contains_passes(self):
        """Test that assertBodyContains passes when key is present in the body."""
        response = Response(correlation_id="test-corr-id")
        response.status(200).send({"message": "OK"})

        self.assertBodyContains(response, "message")

    def test_assert_body_contains_fails(self):
        """Test that assertBodyContains fails when key is not present in the body."""
        response = Response(correlation_id="test-corr-id")
        response.status(200).send({"data": "OK"})

        with self.assertRaises(AssertionError):
            self.assertBodyContains(response, "message")

    def test_assert_has_header_passes(self):
        """Test that assertHasHeader passes when header is present."""
        response = Response(correlation_id="test-corr-id")
        response.set_header("X-Test-Header", "SomeValue")

        self.assertHasHeader(response, "X-Test-Header")

    def test_assert_has_header_fails(self):
        """Test that assertHasHeader fails when header is not present."""
        response = Response(correlation_id="test-corr-id")

        with self.assertRaises(AssertionError):
            self.assertHasHeader(response, "X-Test-Header")

    def test_assert_bad_request(self):
        """Test that assertBadRequest passes when status is 400."""
        response = Response(correlation_id="test-corr-id")
        response.status(400).send({"error": "Bad Request"})

        self.assertBadRequest(response)

    def test_assert_not_found(self):
        """Test that assertNotFound passes when status is 404."""
        response = Response(correlation_id="test-corr-id")
        response.status(404).send({"error": "Not Found"})

        self.assertNotFound(response)

    def test_assert_unauthorized(self):
        """Test that assertUnauthorized passes when status is 401."""
        response = Response(correlation_id="test-corr-id")
        response.status(401).send({"error": "Unauthorized"})

        self.assertUnauthorized(response)

    def test_assert_forbidden(self):
        """Test that assertForbidden passes when status is 403."""
        response = Response(correlation_id="test-corr-id")
        response.status(403).send({"error": "Forbidden"})

        self.assertForbidden(response)

    def test_assert_internal_server_error(self):
        """Test that assertInternalServerError passes when status is 500."""
        response = Response(correlation_id="test-corr-id")
        response.status(500).send({"error": "Internal Server Error"})

        self.assertInternalServerError(response)


if __name__ == '__main__':
    unittest.main()
