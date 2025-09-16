"""
Decorators for error handling and resilience
"""

import functools
import asyncio
import time
from typing import Callable, Any, Optional, Dict, Type
from app.core.errors import (
    ViperMindError, AIServiceError, DatabaseError, 
    error_handler, fallback_content, ErrorType
)

def with_fallback(fallback_func: Optional[Callable] = None, 
                 error_types: tuple = (AIServiceError,)):
    """
    Decorator that provides fallback functionality when specific errors occur
    
    Args:
        fallback_func: Function to call when error occurs
        error_types: Tuple of error types that should trigger fallback
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except error_types as e:
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                else:
                    # Use default fallback based on function name
                    return _get_default_fallback(func.__name__, *args, **kwargs)
            except Exception as e:
                # Log unexpected errors
                error_handler.handle_error(e, {"function": func.__name__})
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                else:
                    return _get_default_fallback(func.__name__, *args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, {"function": func.__name__})
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, 
                    delay: float = 1.0, 
                    backoff_factor: float = 2.0,
                    retry_on: tuple = (AIServiceError, DatabaseError)):
    """
    Decorator that retries function execution on specific failures
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        retry_on: Tuple of error types that should trigger retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        # Log final failure
                        error_handler.handle_error(e, {
                            "function": func.__name__,
                            "attempts": attempt + 1,
                            "final_failure": True
                        })
                        raise
                except Exception as e:
                    # Don't retry on unexpected errors
                    error_handler.handle_error(e, {"function": func.__name__})
                    raise
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        error_handler.handle_error(e, {
                            "function": func.__name__,
                            "attempts": attempt + 1,
                            "final_failure": True
                        })
                        raise
                except Exception as e:
                    error_handler.handle_error(e, {"function": func.__name__})
                    raise
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def timeout_after(seconds: float):
    """
    Decorator that adds timeout to function execution
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise ViperMindError(
                    message=f"Function {func.__name__} timed out after {seconds} seconds",
                    error_type=ErrorType.TIMEOUT_ERROR,
                    error_code="FUNCTION_TIMEOUT",
                    recovery_suggestions=[
                        "Try again with a simpler request",
                        "Check your network connection",
                        "Contact support if the issue persists"
                    ]
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we can't easily implement timeout
            # without threading, so we'll just call the function
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def handle_ai_errors(service_name: str = "AI Service"):
    """
    Decorator specifically for handling AI service errors
    
    Args:
        service_name: Name of the AI service for error messages
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Convert any AI-related error to AIServiceError
                if "openai" in str(e).lower() or "api" in str(e).lower():
                    raise AIServiceError(
                        message=str(e),
                        service_name=service_name,
                        context={"function": func.__name__}
                    )
                else:
                    raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "openai" in str(e).lower() or "api" in str(e).lower():
                    raise AIServiceError(
                        message=str(e),
                        service_name=service_name,
                        context={"function": func.__name__}
                    )
                else:
                    raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_performance(threshold_seconds: float = 1.0):
    """
    Decorator that logs slow function executions
    
    Args:
        threshold_seconds: Log if execution takes longer than this
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    error_handler.logger.logger.warning(
                        f"Slow execution: {func.__name__} took {execution_time:.2f}s"
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                error_handler.handle_error(e, {
                    "function": func.__name__,
                    "execution_time": execution_time
                })
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    error_handler.logger.logger.warning(
                        f"Slow execution: {func.__name__} took {execution_time:.2f}s"
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                error_handler.handle_error(e, {
                    "function": func.__name__,
                    "execution_time": execution_time
                })
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def _get_default_fallback(func_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Get default fallback response based on function name"""
    
    fallback_responses = {
        "generate_lesson": {
            "success": False,
            "content": fallback_content.get_fallback_lesson("python_basics"),
            "fallback_used": True,
            "message": "Using pre-generated lesson content due to AI service unavailability"
        },
        "generate_questions": {
            "success": False,
            "questions": fallback_content.get_fallback_questions("python_basics"),
            "fallback_used": True,
            "message": "Using pre-generated questions due to AI service unavailability"
        },
        "generate_hint": {
            "success": False,
            "hint": fallback_content.get_fallback_hint(),
            "fallback_used": True,
            "message": "Using generic hint due to AI service unavailability"
        }
    }
    
    return fallback_responses.get(func_name, {
        "success": False,
        "fallback_used": True,
        "message": "Service temporarily unavailable. Please try again later."
    })

# Convenience decorators combining multiple features
def resilient_ai_function(service_name: str = "AI Service", 
                         max_retries: int = 2,
                         timeout_seconds: float = 30.0):
    """
    Combines AI error handling, retries, timeout, and fallback
    """
    def decorator(func: Callable) -> Callable:
        # Apply decorators in reverse order (innermost first)
        decorated = func
        decorated = handle_ai_errors(service_name)(decorated)
        decorated = timeout_after(timeout_seconds)(decorated)
        decorated = retry_on_failure(max_retries=max_retries)(decorated)
        decorated = with_fallback()(decorated)
        decorated = log_performance()(decorated)
        return decorated
    return decorator