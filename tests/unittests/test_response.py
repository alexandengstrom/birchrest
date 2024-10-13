# type: ignore

import unittest
from birchrest.http import Response, HttpStatus
import json


class TestResponse(unittest.TestCase):

    def setUp(self):
        """Set up a new Response object for each test."""
        self.response = Response()

    def test_initialization(self):
        """Test initial state of the Response object."""
        self.assertEqual(self.response._status_code, 200)
        self.assertEqual(self.response._headers['Content-Type'], 'text/html')
        self.assertEqual(self.response._body, '')
        self.assertFalse(self.response._is_sent)

    def test_status_code_setter(self):
        """Test that setting the status code works properly."""
        self.response.status(404)
        self.assertEqual(self.response._status_code, 404)

        self.response.status(HttpStatus.NOT_FOUND)
        self.assertEqual(self.response._status_code, HttpStatus.NOT_FOUND.value)

    def test_set_header(self):
        """Test that setting a header works as expected."""
        self.response.set_header('X-Test-Header', 'TestValue')
        self.assertEqual(self.response._headers['X-Test-Header'], 'TestValue')

    def test_send_json_body(self):
        """Test sending a JSON body and setting content type and length."""
        data = {"message": "Hello, world"}
        self.response.send(data)

        expected_body = json.dumps(data)
        self.assertEqual(self.response._body, expected_body)

        self.assertEqual(self.response._headers['Content-Type'], 'application/json')

        self.assertEqual(self.response._headers['Content-Length'], str(len(expected_body)))

        self.assertTrue(self.response._is_sent)

    def test_send_twice_raises_exception(self):
        self.response.send({"message": "First response"})
        
        with self.assertRaises(Exception) as context:
            self.response.send({"message": "Second response"})
        
        self.assertEqual(str(context.exception), "Request was sent twice")

    def test_end_response_format(self):
        data = {"message": "Hello, world"}
        self.response.status(200).send(data)
        raw_response = self.response.end()

        status_line = "HTTP/1.1 200 OK\r\n"
        content_type_header = "Content-Type: application/json\r\n"
        content_length_header = f"Content-Length: {len(json.dumps(data))}\r\n"

        expected_raw_response = (
            status_line +
            content_type_header +
            content_length_header +
            "\r\n" +
            json.dumps(data)
        )

        self.assertEqual(raw_response, expected_raw_response)

    def test_response_repr(self):
        self.response.status(200).send({"message": "Hello"})
        repr_str = repr(self.response)
        self.assertIn("Response 200", repr_str)
        self.assertIn("bytes", repr_str)


if __name__ == "__main__":
    unittest.main()
