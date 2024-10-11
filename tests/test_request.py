# type: ignore

import unittest
from datetime import datetime
from birchrest.http import Request
import json

class TestRequest(unittest.TestCase):

    def setUp(self):
        self.headers = {
            "content-type": "application/json",
            "content-length": "18",
            "user-agent": "unittest-client"
        }
        self.body = '{"name": "Alice"}'
        self.raw_request_data = (
            "POST /api/v1/users HTTP/1.1\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: 18\r\n"
            "User-Agent: unittest-client\r\n\r\n"
            '{"name": "Alice"}'
        )
        self.client_address = "127.0.0.1"

    def test_request_initialization(self):
        req = Request(
            method="GET",
            path="/api/v1/users?name=alice",
            version="HTTP/1.1",
            headers=self.headers,
            body=self.body,
            client_address=self.client_address
        )
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.clean_path, "/api/v1/users")
        self.assertEqual(req.queries["name"], "alice")
        self.assertEqual(req.client_address, self.client_address)
        self.assertIsInstance(req.received, datetime)
        self.assertEqual(req.body, {"name": "Alice"})

    def test_parse_static_method(self):
        req = Request.parse(self.raw_request_data, self.client_address)
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.path, "/api/v1/users")
        self.assertEqual(req.version, "HTTP/1.1")
        self.assertEqual(req.headers["content-type"], "application/json")
        self.assertEqual(req.get_header("content-length"), "18")
        self.assertEqual(req.body, {"name": "Alice"})
        self.assertEqual(req.client_address, self.client_address)

    def test_get_header(self):
        req = Request(
            method="GET",
            path="/api/v1/users",
            version="HTTP/1.1",
            headers=self.headers,
            body=self.body,
            client_address=self.client_address
        )
        self.assertEqual(req.get_header("Content-Type"), "application/json")
        self.assertEqual(req.get_header("content-length"), "18")
        self.assertIsNone(req.get_header("non-existent-header"))

    def test_request_repr(self):
        req = Request(
            method="POST",
            path="/api/v1/users",
            version="HTTP/1.1",
            headers=self.headers,
            body=self.body,
            client_address=self.client_address
        )
        repr_str = repr(req)
        self.assertIn("Method: POST", repr_str)
        self.assertIn("Correlation ID:", repr_str)
        self.assertIn("Path: /api/v1/users", repr_str)
        self.assertIn("Client Address: 127.0.0.1", repr_str)
        self.assertIn('"name": "Alice"', repr_str)

    def test_query_parameters_parsing(self):
        req = Request(
            method="GET",
            path="/api/v1/users?name=alice&age=30",
            version="HTTP/1.1",
            headers=self.headers,
            body=None,
            client_address=self.client_address
        )
        self.assertEqual(req.queries["name"], "alice")
        self.assertEqual(req.queries["age"], "30")

    def test_parse_empty_body(self):
        raw_data_with_empty_body = (
            "GET /api/v1/users HTTP/1.1\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: 0\r\n"
            "User-Agent: unittest-client\r\n\r\n"
        )
        req = Request.parse(raw_data_with_empty_body, self.client_address)
        self.assertIsNone(req.body)
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.clean_path, "/api/v1/users")

if __name__ == "__main__":
    unittest.main()
