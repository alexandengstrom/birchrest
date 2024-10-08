from typing import Dict, Optional, List, Any
from urllib.parse import urlparse, parse_qs
import json
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime


class Request:
    def __init__(
        self,
        method: str,
        path: str,
        version: str,
        headers: Dict[str, str],
        body: Optional[str],
        client_address: str
    ) -> None:
        """
        Represents an HTTP request.

        :param method: The HTTP method (GET, POST, etc.)
        :param path: The requested path
        :param version: The HTTP version (e.g., HTTP/1.1)
        :param headers: A dictionary of HTTP request headers
        :param body: The request body, if any
        :param client_address: The address of the client making the request
        """
        self.method: str = method
        self.path: str = path
        self.version: str = version
        self.headers: Dict[str, str] = headers
        self.body: Optional[str] = json.loads(body) if body else None
        self.client_address: str = client_address
        self.params: Dict[str, str] = {}
        self.correlation_id: str = str(uuid.uuid4())
        self.user: Optional[Any] = None
        self.received = datetime.now()

        parsed_url = urlparse(self.path)
        parsed_queries: Dict[str, List[str]] = parse_qs(parsed_url.query)
        self.queries = {}

        for (key, value) in parsed_queries.items():
            self.queries[key] = value[0] if len(value) < 2 else value

        self.clean_path: str = parsed_url.path

    @staticmethod
    def parse(raw_data: str, client_address: str) -> 'Request':
        """
        Static method to create a Request object from raw HTTP request data.

        :param raw_data: The raw HTTP request as a string
        :param client_address: The address of the client making the request
        :return: A Request object
        """
        lines = raw_data.splitlines()

        request_line = lines[0].split()

        method = request_line[0]
        path = request_line[1]
        version = request_line[2]

        headers = {}
        for i, line in enumerate(lines[1:], start=1):
            if line == '':
                break
            header_name, header_value = line.split(':', 1)
            headers[header_name.strip().lower()] = header_value.strip()

        body = ''

        if 'content-length' in headers:
            content_length = int(headers['content-length'])
            body = raw_data.split('\r\n\r\n', 1)[1]
            if len(body) > content_length:
                body = body[:content_length]

        return Request(method, path, version, headers, body, client_address)

    def get_header(self, header_name: str) -> Optional[str]:
        """
        Get a specific header by name, case-insensitive.

        :param header_name: The name of the header to retrieve
        :return: The header value, or None if not found
        """
        return self.headers.get(header_name.lower())

    def __repr__(self) -> str:
        def serialize_body(body: Any) -> str:
            if is_dataclass(body) and not isinstance(body, type):
                return json.dumps(asdict(body), indent=4)
            return json.dumps(body, indent=4) if body else 'None'

        return (
            f"<Request>\n"
            f"  Method: {self.method}\n"
            f"  Correlation ID: {self.correlation_id}\n"
            f"  Path: {self.clean_path}\n"
            f"  Full Path: {self.path}\n"
            f"  HTTP Version: {self.version}\n"
            f"  Client Address: {self.client_address}\n"
            f"  Headers: {json.dumps(self.headers, indent=4)}\n"
            f"  Query Parameters: {json.dumps(self.queries, indent=4)}\n"
            f"  Path Parameters: {json.dumps(self.params, indent=4)}\n"
            f"  Body: {serialize_body(self.body) if self.body else 'None'}\n"
        )