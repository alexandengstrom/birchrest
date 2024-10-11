# type: ignore

import unittest
from unittest.mock import Mock, patch
from birchrest.http.request import Request
from birchrest.http.response import Response
from birchrest.app.birchrest import BirchRest
from birchrest.unittest import TestAdapter
from typing import Dict, Optional, Any


class TestTestAdapter(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up the TestAdapter with a mocked BirchRest app."""
        self.mock_app = Mock(spec=BirchRest)
        self.adapter = TestAdapter(self.mock_app)
        self.mock_response = Mock(spec=Response)
        self.mock_app.handle_request.return_value = self.mock_response

    def _assert_request(self, method: str, path: str, headers: Dict[str, str], body: Optional[Any]):
        """Helper method to check the generated request."""
        self.mock_app.handle_request.assert_called_once()
        generated_request = self.mock_app.handle_request.call_args[0][0]

        self.assertEqual(generated_request.method, method)
        self.assertEqual(generated_request.path, path)
        self.assertEqual(generated_request.headers, headers)
        self.assertEqual(generated_request.body, body)
        self.assertEqual(generated_request.version, "HTTP/1.1")

    async def test_get_request(self):
        """Test that a GET request is correctly generated and handled."""
        path = "/test-get"
        headers = {"Authorization": "Bearer token"}
        
        response = await self.adapter.get(path, headers)
        self.assertEqual(response, self.mock_response)
        
        self._assert_request("GET", path, headers, None)

    async def test_post_request(self):
        """Test that a POST request is correctly generated and handled."""
        path = "/test-post"
        headers = {"Content-Type": "application/json"}
        body = {"key": "value"}

        response = await self.adapter.post(path, headers, body)
        self.assertEqual(response, self.mock_response)

        self._assert_request("POST", path, headers, body)

    async def test_put_request(self):
        """Test that a PUT request is correctly generated and handled."""
        path = "/test-put"
        headers = {"Content-Type": "application/json"}
        body = {"updated_key": "updated_value"}

        response = await self.adapter.put(path, headers, body)
        self.assertEqual(response, self.mock_response)

        self._assert_request("PUT", path, headers, body)

    async def test_patch_request(self):
        """Test that a PATCH request is correctly generated and handled."""
        path = "/test-patch"
        headers = {"Content-Type": "application/json"}
        body = {"patched_key": "patched_value"}

        response = await self.adapter.patch(path, headers, body)
        self.assertEqual(response, self.mock_response)

        self._assert_request("PATCH", path, headers, body)

    async def test_delete_request(self):
        """Test that a DELETE request is correctly generated and handled."""
        path = "/test-delete"
        headers = {"Authorization": "Bearer token"}
        
        response = await self.adapter.delete(path, headers)
        self.assertEqual(response, self.mock_response)

        self._assert_request("DELETE", path, headers, None)

    async def test_head_request(self):
        """Test that a HEAD request is correctly generated and handled."""
        path = "/test-head"
        headers = {"Authorization": "Bearer token"}
        
        response = await self.adapter.head(path, headers)
        self.assertEqual(response, self.mock_response)

        self._assert_request("HEAD", path, headers, None)

    async def test_options_request(self):
        """Test that an OPTIONS request is correctly generated and handled."""
        path = "/test-options"
        headers = {"Authorization": "Bearer token"}
        
        response = await self.adapter.options(path, headers)
        self.assertEqual(response, self.mock_response)

        self._assert_request("OPTIONS", path, headers, None)


if __name__ == "__main__":
    unittest.main()
