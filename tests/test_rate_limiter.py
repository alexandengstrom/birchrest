# type: ignore

import unittest
from unittest.mock import Mock, patch, AsyncMock
import time
from collections import defaultdict
from birchrest.middlewares import RateLimiter
from birchrest.http import Request, Response
from birchrest.types import NextFunction


class TestRateLimiter(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up the RateLimiter instance before each test."""
        self.rate_limiter = RateLimiter(max_requests=2, window_seconds=10)

    def test_initial_state(self):
        """Test the initial state of the RateLimiter."""
        self.assertEqual(self.rate_limiter.max_requests, 2)
        self.assertEqual(self.rate_limiter.window_seconds, 10)
        self.assertIsInstance(self.rate_limiter.request_log, defaultdict)

    def test_clean_old_requests(self):
        """Test that old requests are properly cleaned up from the log."""
        client_id = '127.0.0.1'
        self.rate_limiter.request_log[client_id] = {
            "timestamps": [time.time() - 20, time.time() - 5],
            "request_count": 2
        }

        self.rate_limiter._clean_old_requests(client_id)

        # After cleaning, only the second request should remain
        self.assertEqual(self.rate_limiter.request_log[client_id]["request_count"], 1)

    def test_all_requests_cleaned(self):
        """Test that all requests are cleaned if they are outside the time window."""
        client_id = '127.0.0.1'
        self.rate_limiter.request_log[client_id] = {
            "timestamps": [time.time() - 20, time.time() - 15],  # All outside the window
            "request_count": 2
        }

        self.rate_limiter._clean_old_requests(client_id)

        # After cleaning, no requests should remain
        self.assertEqual(self.rate_limiter.request_log[client_id]["request_count"], 0)

    @patch('time.time', return_value=1000.0)
    async def test_rate_limiter_allows_request(self, mock_time):
        """Test that the rate limiter allows a request if within the limit."""
        mock_request = Mock(spec=Request)
        mock_request.client_address = '127.0.0.1'

        mock_response = Mock(spec=Response)
        mock_next = AsyncMock(spec=NextFunction)

        # Make a first request
        await self.rate_limiter(mock_request, mock_response, mock_next)

        # Ensure next function was called, meaning request was allowed
        mock_next.assert_called_once()
        self.assertEqual(self.rate_limiter.request_log['127.0.0.1']["request_count"], 1)

    @patch('time.time', return_value=1000.0)
    async def test_rate_limiter_blocks_after_max_requests(self, mock_time):
        """Test that the rate limiter blocks a request after max requests are exceeded."""
        mock_request = Mock(spec=Request)
        mock_request.client_address = '127.0.0.1'

        mock_response = Mock(spec=Response)
        mock_response.status.return_value = mock_response
        mock_response.send.return_value = mock_response
        mock_next = AsyncMock(spec=NextFunction)

        await self.rate_limiter(mock_request, mock_response, mock_next)

        await self.rate_limiter(mock_request, mock_response, mock_next)

        await self.rate_limiter(mock_request, mock_response, mock_next)
        
        self.assertEqual(mock_next.call_count, 2)

        mock_response.status.assert_called_with(429)
        mock_response.send.assert_called_with({"error": "Too Many Requests"})



    @patch('time.time', return_value=1000.0)
    async def test_rate_limiter_allows_after_time_window(self, mock_time):
        """Test that the rate limiter allows requests after the time window expires."""
        mock_request = Mock(spec=Request)
        mock_request.client_address = '127.0.0.1'

        mock_response = Mock(spec=Response)
        mock_next = AsyncMock(spec=NextFunction)

        await self.rate_limiter(mock_request, mock_response, mock_next)
        await self.rate_limiter(mock_request, mock_response, mock_next)

        with patch('time.time', return_value=1011.0):
            await self.rate_limiter(mock_request, mock_response, mock_next)

        mock_next.assert_called()

    @patch('time.time', return_value=1000.0)
    def test_rate_limiter_resets_request_count(self, mock_time):
        """Test that the request count resets after the time window expires."""
        client_id = '127.0.0.1'
        self.rate_limiter.request_log[client_id] = {
            "timestamps": [1000.0],
            "request_count": 1
        }

        with patch('time.time', return_value=1011.0):
            self.rate_limiter._clean_old_requests(client_id)

        self.assertEqual(self.rate_limiter.request_log[client_id]["request_count"], 0)


if __name__ == '__main__':
    unittest.main()
