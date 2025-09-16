"""
Comprehensive error handling system for ViperMind
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import traceback
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorType(str, Enum):
    """Error type classifications"""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    DATABASE_ERROR = "database_error"
    AI_SERVICE_ERROR = "ai_service_error"
    EXTERNAL_API_ERROR = "external_api_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    INTERNAL_ERROR = "internal_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"

class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorContext(BaseModel):
    """Error context information"""
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    request_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    additional_data: Dict[str, Any] = {}

class ErrorDetail(BaseModel):
    """Detailed error information"""
    error_type: ErrorType
    error_code: str
    message: str
    user_message: str
    severity: ErrorSeverity
    context: ErrorContext
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = []
    fallback_available: bool = False
    retry_after: Optional[int] = None  # seconds

class ViperMindError(Exception):
    """Base exception class for ViperMind application"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_ERROR,
        error_code: str = "UNKNOWN_ERROR",
        user_message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None,
        fallback_available: bool = False,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.error_type = error_type
        self.error_code = error_code
        self.user_message = user_message or self._get_default_user_message()
        self.severity = severity
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.fallback_available = fallback_available
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()
    
    def _get_default_user_message(self) -> str:
        """Get default user-friendly message based on error type"""
        messages = {
            ErrorType.VALIDATION_ERROR: "Please check your input and try again.",
            ErrorType.AUTHENTICATION_ERROR: "Please log in to continue.",
            ErrorType.AUTHORIZATION_ERROR: "You don't have permission to perform this action.",
            ErrorType.NOT_FOUND_ERROR: "The requested resource was not found.",
            ErrorType.DATABASE_ERROR: "We're experiencing technical difficulties. Please try again later.",
            ErrorType.AI_SERVICE_ERROR: "Our AI service is temporarily unavailable. We'll use alternative content.",
            ErrorType.EXTERNAL_API_ERROR: "External service is unavailable. Please try again later.",
            ErrorType.RATE_LIMIT_ERROR: "Too many requests. Please wait a moment and try again.",
            ErrorType.NETWORK_ERROR: "Network connection issue. Please check your connection.",
            ErrorType.TIMEOUT_ERROR: "Request timed out. Please try again.",
            ErrorType.INTERNAL_ERROR: "Something went wrong. Our team has been notified."
        }
        return messages.get(self.error_type, "An unexpected error occurred.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error_type": self.error_type.value,
            "error_code": self.error_code,
            "message": str(self),
            "user_message": self.user_message,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "recovery_suggestions": self.recovery_suggestions,
            "fallback_available": self.fallback_available,
            "retry_after": self.retry_after,
            "context": self.context
        }

class AIServiceError(ViperMindError):
    """AI service specific errors"""
    
    def __init__(self, message: str, service_name: str = "OpenAI", **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.AI_SERVICE_ERROR,
            error_code=f"AI_SERVICE_{service_name.upper()}_ERROR",
            user_message=f"AI service ({service_name}) is temporarily unavailable. Using fallback content.",
            fallback_available=True,
            recovery_suggestions=[
                "Try again in a few moments",
                "The system will use pre-generated content as a fallback",
                "Contact support if the issue persists"
            ],
            **kwargs
        )
        self.service_name = service_name

class DatabaseError(ViperMindError):
    """Database specific errors"""
    
    def __init__(self, message: str, operation: str = "unknown", **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.DATABASE_ERROR,
            error_code=f"DATABASE_{operation.upper()}_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery_suggestions=[
                "Please try again in a moment",
                "If the issue persists, contact support",
                "Your progress has been saved up to this point"
            ],
            **kwargs
        )
        self.operation = operation

class ValidationError(ViperMindError):
    """Input validation errors"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            recovery_suggestions=[
                "Please check your input and try again",
                "Make sure all required fields are filled",
                "Verify that your input meets the specified format"
            ],
            **kwargs
        )
        self.field = field

class RateLimitError(ViperMindError):
    """Rate limiting errors"""
    
    def __init__(self, message: str, retry_after: int = 60, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.RATE_LIMIT_ERROR,
            error_code="RATE_LIMIT_EXCEEDED",
            retry_after=retry_after,
            recovery_suggestions=[
                f"Please wait {retry_after} seconds before trying again",
                "Consider reducing the frequency of your requests",
                "Contact support if you need higher rate limits"
            ],
            **kwargs
        )

class ErrorLogger:
    """Centralized error logging system"""
    
    def __init__(self):
        self.logger = logging.getLogger("vipermind.errors")
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_error(self, error: ViperMindError, context: Optional[ErrorContext] = None):
        """Log error with appropriate level based on severity"""
        
        error_data = {
            "error_type": error.error_type.value,
            "error_code": error.error_code,
            "message": str(error),
            "severity": error.severity.value,
            "timestamp": error.timestamp.isoformat(),
            "context": context.dict() if context else error.context
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_data}")
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {error_data}")
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {error_data}")
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {error_data}")
    
    def log_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None):
        """Log unexpected exceptions"""
        
        error_data = {
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "stack_trace": traceback.format_exc(),
            "context": context or {}
        }
        
        self.logger.error(f"UNHANDLED EXCEPTION: {error_data}")

class ErrorHandler:
    """Central error handling and recovery system"""
    
    def __init__(self):
        self.logger = ErrorLogger()
        self.fallback_content = FallbackContentManager()
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorDetail:
        """Handle any error and return structured error detail"""
        
        if isinstance(error, ViperMindError):
            # Log the custom error
            error_context = ErrorContext(
                timestamp=datetime.utcnow(),
                additional_data=context or {}
            )
            self.logger.log_error(error, error_context)
            
            return ErrorDetail(
                error_type=error.error_type,
                error_code=error.error_code,
                message=str(error),
                user_message=error.user_message,
                severity=error.severity,
                context=error_context,
                recovery_suggestions=error.recovery_suggestions,
                fallback_available=error.fallback_available,
                retry_after=error.retry_after
            )
        
        else:
            # Handle unexpected exceptions
            self.logger.log_exception(error, context)
            
            error_context = ErrorContext(
                timestamp=datetime.utcnow(),
                additional_data=context or {}
            )
            
            return ErrorDetail(
                error_type=ErrorType.INTERNAL_ERROR,
                error_code="UNEXPECTED_ERROR",
                message=str(error),
                user_message="An unexpected error occurred. Our team has been notified.",
                severity=ErrorSeverity.HIGH,
                context=error_context,
                stack_trace=traceback.format_exc(),
                recovery_suggestions=[
                    "Please try again in a moment",
                    "If the issue persists, contact support",
                    "Try refreshing the page"
                ],
                fallback_available=False
            )
    
    def to_http_exception(self, error: ViperMindError) -> HTTPException:
        """Convert ViperMind error to FastAPI HTTPException"""
        
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
        
        status_code = status_codes.get(error.error_type, 500)
        
        return HTTPException(
            status_code=status_code,
            detail=error.to_dict()
        )

class FallbackContentManager:
    """Manages fallback content when AI services are unavailable"""
    
    def __init__(self):
        self.fallback_lessons = self._load_fallback_lessons()
        self.fallback_questions = self._load_fallback_questions()
        self.fallback_hints = self._load_fallback_hints()
    
    def _load_fallback_lessons(self) -> Dict[str, Any]:
        """Load pre-generated lesson content"""
        return {
            "python_basics": {
                "title": "Python Basics",
                "content": "Python is a powerful, easy-to-learn programming language...",
                "examples": ["print('Hello, World!')", "x = 5\nprint(x)"],
                "key_points": ["Python is interpreted", "Indentation matters", "Dynamic typing"]
            },
            "variables": {
                "title": "Variables in Python",
                "content": "Variables are used to store data values...",
                "examples": ["name = 'Alice'", "age = 25", "is_student = True"],
                "key_points": ["No declaration needed", "Case sensitive", "Multiple assignment"]
            }
        }
    
    def _load_fallback_questions(self) -> Dict[str, Any]:
        """Load pre-generated assessment questions"""
        return {
            "python_basics": [
                {
                    "question": "What is Python?",
                    "options": [
                        "A programming language",
                        "A type of snake",
                        "A web browser",
                        "An operating system"
                    ],
                    "correct_answer": 0,
                    "explanation": "Python is a high-level programming language."
                }
            ]
        }
    
    def _load_fallback_hints(self) -> Dict[str, Any]:
        """Load pre-generated hints"""
        return {
            "general": {
                "hint_text": "Think about the core concept being tested. Break down the problem into smaller steps.",
                "encouragement": "You're on the right track! Keep thinking through it step by step."
            }
        }
    
    def get_fallback_lesson(self, topic: str) -> Dict[str, Any]:
        """Get fallback lesson content for a topic"""
        return self.fallback_lessons.get(topic, self.fallback_lessons.get("python_basics"))
    
    def get_fallback_questions(self, topic: str, count: int = 4) -> List[Dict[str, Any]]:
        """Get fallback questions for a topic"""
        questions = self.fallback_questions.get(topic, self.fallback_questions.get("python_basics", []))
        return questions[:count] if questions else []
    
    def get_fallback_hint(self, context: str = "general") -> Dict[str, Any]:
        """Get fallback hint"""
        return self.fallback_hints.get(context, self.fallback_hints["general"])

# Global instances
error_handler = ErrorHandler()
fallback_content = FallbackContentManager()