"""Exception handling middleware for the application.

Intercepts exceptions raised during request processing and returns
appropriate JSON responses with detailed error information.
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from fastapi import Request, Response
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.exceptions import (
    IngestionError,
    ProviderNotConfiguredError,
    SearchError,
    VectorStoreError,
)

logger = logging.getLogger("semantic_search")

EXCEPTION_STATUS_MAP = {
    ProviderNotConfiguredError: 503,
    IngestionError: 500,
    SearchError: 500,
    VectorStoreError: 500,
}


class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions in the FastAPI application.

    Intercepts exceptions raised during request processing and returns
    appropriate JSON responses. Handles validation errors, custom domain
    exceptions and generic exceptions with detailed error information.
    """

    def __init__(self, app: ASGIApp, custom_logger=None):
        super().__init__(app)
        self.logger = custom_logger or logger

    def safe_serialize(self, obj: Any) -> Any:
        """Safely serialize objects, converting non-serializable objects to string."""
        if hasattr(obj, "__dict__"):
            try:
                return {
                    key: self.safe_serialize(value)
                    for key, value in obj.__dict__.items()
                }
            except Exception:
                return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [self.safe_serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.safe_serialize(value) for key, value in obj.items()}
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process incoming requests and handle exceptions."""
        try:
            response = await call_next(request)
            return response
        except ResponseValidationError as exc:
            error_time = datetime.now(timezone.utc).isoformat()
            self.logger.error(
                "Validation Error on %s %s: %s",
                request.method,
                request.url.path,
                exc.errors(),
            )
            return self._create_error_response(
                status_code=422,
                content={
                    "detail": "Validation Error",
                    "errors": self.safe_serialize(exc.errors()),
                    "timestamp": error_time,
                },
            )
        except tuple(EXCEPTION_STATUS_MAP.keys()) as exc:
            status_code = EXCEPTION_STATUS_MAP[type(exc)]
            error_time = datetime.now(timezone.utc).isoformat()
            self._log_exception_details(request, exc, error_time)
            return self._create_error_response(
                status_code=status_code,
                content=self.safe_serialize(
                    {
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                        "timestamp": error_time,
                        "request_path": str(request.url.path),
                        "request_method": request.method,
                    }
                ),
            )
        except Exception as exc:
            error_traceback = traceback.format_exc()
            error_time = datetime.now(timezone.utc).isoformat()
            self._log_exception_details(request, exc, error_time, error_traceback)

            return self._create_error_response(
                status_code=500,
                content=self.safe_serialize(
                    {
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                        "traceback": error_traceback,
                        "timestamp": error_time,
                        "request_path": str(request.url.path),
                        "request_method": request.method,
                    }
                ),
            )

    def _log_exception_details(
        self,
        request: Request,
        exc: Exception,
        error_time: str,
        error_traceback: str | None = None,
    ) -> None:
        """Log detailed exception information."""
        self.logger.error("=== EXCEPTION DETAILS ===")
        self.logger.error("Request: %s %s", request.method, request.url.path)
        self.logger.error("Query Params: %s", dict(request.query_params))
        self.logger.error("Exception Type: %s", type(exc).__name__)
        self.logger.error("Exception Message: %s", str(exc))
        self.logger.error("Timestamp: %s", error_time)
        if error_traceback:
            self.logger.error("Full Traceback:")
            self.logger.error(error_traceback)
        self.logger.error("=== END EXCEPTION DETAILS ===")

    @staticmethod
    def _create_error_response(status_code: int, content: dict) -> JSONResponse:
        """Create a JSON error response."""
        return JSONResponse(status_code=status_code, content=content)
