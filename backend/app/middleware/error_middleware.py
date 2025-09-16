"""
Error handling middleware for ViperMind FastAPI application
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Callable
from app.core.errors import error_handler, ViperMindError, ErrorContext, ErrorType

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle all application errors consistently"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add request ID and timing to response headers
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as exc:
            # Create error context
            context = ErrorContext(
                user_id=getattr(request.state, 'user_id', None),
                endpoint=str(request.url.path),
                request_id=request_id,
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host if request.client else None,
                timestamp=time.time(),
                additional_data={
                    "method": request.method,
                    "query_params": dict(request.query_params),
                    "process_time": time.time() - start_time
                }
            )
            
            # Handle the error
            error_detail = error_handler.handle_error(exc, context.dict())
            
            # Determine HTTP status code
            status_codes = {
                ErrorType.VALIDATION_ERROR: 400,
                ErrorType.AUTHENTICATION_ERROR: 401,
                ErrorType.AUTHORIZATION_ERROR: 403,
                ErrorType.NOT_FOUND_ERROR: 404,
                ErrorType.RATE_LIMIT_ERROR: 429,
                ErrorType.DATABASE_ERROR: 500,
                ErrorType.AI_SERVICE_ERROR: 503,
                ErrorType.EXTERNAL_API_ERROR: 503,
                ErrorType.NETWORK_ERROR: 503,
                ErrorType.TIMEOUT_ERROR: 504,
                ErrorType.INTERNAL_ERROR: 500
            }
            
            status_code = status_codes.get(error_detail.error_type, 500)
            
            # Create error response
            error_response = {
                "success": False,
                "error": {
                    "type": error_detail.error_type.value,
                    "code": error_detail.error_code,
                    "message": error_detail.user_message,
                    "details": error_detail.message if status_code < 500 else None,
                    "request_id": request_id,
                    "timestamp": error_detail.context.timestamp.isoformat(),
                    "recovery_suggestions": error_detail.recovery_suggestions,
                    "fallback_available": error_detail.fallback_available,
                    "retry_after": error_detail.retry_after
                }
            }
            
            # Add stack trace for development
            if hasattr(request.app.state, 'debug') and request.app.state.debug:
                error_response["error"]["stack_trace"] = error_detail.stack_trace
            
            return JSONResponse(
                status_code=status_code,
                content=error_response,
                headers={
                    "X-Request-ID": request_id,
                    "X-Error-Type": error_detail.error_type.value,
                    "X-Process-Time": str(time.time() - start_time)
                }
            )

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Reset counts every minute
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_count = self.request_counts.get(client_id, 0)
        if current_count >= self.requests_per_minute:
            error_response = {
                "success": False,
                "error": {
                    "type": "rate_limit_error",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60 - (current_time - self.last_reset)
                }
            }
            return JSONResponse(
                status_code=429,
                content=error_response,
                headers={"Retry-After": "60"}
            )
        
        # Increment counter
        self.request_counts[client_id] = current_count + 1
        
        # Continue with request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - self.request_counts[client_id])
        response.headers["X-RateLimit-Reset"] = str(int(self.last_reset + 60))
        
        return response