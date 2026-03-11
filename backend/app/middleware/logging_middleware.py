"""Logging middleware for the application.

Logs all incoming requests and outgoing responses for debugging and monitoring.
"""

import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("semantic_search")

SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses with timing and details."""

    def __init__(self, app: ASGIApp, custom_logger=None):
        super().__init__(app)
        self.logger = custom_logger or logger

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process incoming requests and log all details."""
        self.logger.info("=== INCOMING REQUEST ===")
        self.logger.info("Method: %s", request.method)
        self.logger.info("URL: %s", request.url)
        self.logger.info("Path: %s", request.url.path)
        self.logger.info("Query Params: %s", dict(request.query_params))
        self.logger.info("Headers: %s", self._safe_headers(request.headers))
        self.logger.info("Client: %s", request.client)

        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self.logger.info("=== OUTGOING RESPONSE ===")
            self.logger.info("Status Code: %s", response.status_code)
            self.logger.info("Process Time: %.4fs", process_time)
            self.logger.info("Headers: %s", dict(response.headers))
            self.logger.info("=== END RESPONSE ===")
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            self.logger.error("=== REQUEST ERROR ===")
            self.logger.error("Error Type: %s", type(exc).__name__)
            self.logger.error("Error Message: %s", str(exc))
            self.logger.error("Process Time: %.4fs", process_time)
            self.logger.error("=== END ERROR ===")
            raise

    @staticmethod
    def _safe_headers(headers) -> dict:
        """Filter out sensitive headers before logging."""
        return {
            k: ("***" if k.lower() in SENSITIVE_HEADERS else v)
            for k, v in headers.items()
        }
