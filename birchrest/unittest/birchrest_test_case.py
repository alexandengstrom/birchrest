import unittest
from birchrest.http.response import Response


class BirchRestTestCase(unittest.IsolatedAsyncioTestCase):
    """
    A custom TestCase class that adds helper methods for asserting BirchRest HTTP responses.

    This class extends unittest.IsolatedAsyncioTestCase and provides additional assertion methods to
    validate HTTP status codes, headers, and response bodies in a simplified manner.
    """

    def assertOk(self, response: Response) -> None:
        """
        Assert that the response status code is in the range of 2xx (successful responses).
        """
        self.assertTrue(
            response._status_code < 300,
            f"Expected status code to be OK, got {response._status_code}",
        )

    def assertNotOk(self, response: Response) -> None:
        """
        Assert that the response status code is not in the range of 2xx (indicating failure).
        """
        self.assertTrue(
            response._status_code >= 300,
            f"Expected status code to indicate failure, got {response._status_code}",
        )

    def assertBadRequest(self, response: Response) -> None:
        """
        Assert that the response status is 400.
        """
        self.assertTrue(
            response._status_code == 400,
            f"Expected status code to be 400, got {response._status_code}",
        )

    def assertNotFound(self, response: Response) -> None:
        """
        Assert that the response status is 404.
        """
        self.assertTrue(
            response._status_code == 404,
            f"Expected status code to be 404, got {response._status_code}",
        )

    def assertUnauthorized(self, response: Response) -> None:
        """
        Assert that the response status is 401.
        """
        self.assertTrue(
            response._status_code == 401,
            f"Expected status code to be 401, got {response._status_code}",
        )

    def assertForbidden(self, response: Response) -> None:
        """
        Assert that the response status is 403.
        """
        self.assertTrue(
            response._status_code == 403,
            f"Expected status code to be 403, got {response._status_code}",
        )

    def assertInternalServerError(self, response: Response) -> None:
        """
        Assert that the response status is 500.
        """
        self.assertTrue(
            response._status_code == 500,
            f"Expected status code to be 500, got {response._status_code}",
        )

    def assertStatus(self, response: Response, expected_status: int) -> None:
        """
        Assert that the response status code matches the expected status.

        :param response: The Response object to check
        :param expected_status: The expected HTTP status code
        """
        self.assertEqual(
            response._status_code,
            expected_status,
            f"Expected status {expected_status}, got {response._status_code}",
        )

    def assertHasHeader(self, response: Response, expected_key: str) -> None:
        """
        Assert that the response has a specific header.
        """
        self.assertTrue(expected_key in response._headers)

    def assertHeader(
        self, response: Response, header_name: str, expected_value: str
    ) -> None:
        """
        Assert that a specific header in the response matches the expected value.

        :param response: The Response object to check
        :param header_name: The name of the header to validate
        :param expected_value: The expected value of the header
        """
        actual_value = response._headers.get(header_name)
        self.assertIsNotNone(
            actual_value, f"Header '{header_name}' not found in response"
        )
        self.assertEqual(
            actual_value,
            expected_value,
            f"Expected header '{header_name}' to have value '{expected_value}', but got '{actual_value}'",
        )

    def assertRedirect(self, response: Response, expected_url: str) -> None:
        """
        Assert that the response status is a redirect (3xx) and the Location header matches the expected URL.
        """
        self.assertTrue(
            300 <= response._status_code < 400,
            f"Expected redirect status code, got {response._status_code}",
        )
        self.assertHeader(response, "Location", expected_url)

    def assertBodyContains(self, response: Response, expected_key: str) -> None:
        """
        Assert that the response body contains a certain property
        """
        self.assertTrue(expected_key in response.body)
