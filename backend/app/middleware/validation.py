"""Input validation middleware for enhanced security."""

import re
from fastapi import HTTPException, status, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and security checks."""
    
    # Patterns for potentially dangerous content
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript protocol
        r'on\w+\s*=',                 # Event handlers
        r'eval\s*\(',                 # eval() calls
        r'document\.',                # Document access
        r'window\.',                  # Window access
        r'expression\s*\(',           # CSS expressions
    ]
    
    # SQL injection patterns (refined to reduce false positives)
    SQL_INJECTION_PATTERNS = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|into|table|database)\b)',
        r'(--|#|\/\*|\*\/)',           # SQL comments
        r'(\'\s*;\s*(drop|delete|update|insert)\s+)',              # Dangerous chained statements
        r'(\bor\s+1\s*=\s*1\b.*\b(or|and)\b)',       # Always true condition with additional logic
        r'(\band\s+1\s*=\s*1\b.*\b(or|and)\b)',      # Always true condition with additional logic
        r'(\'\s*or\s*\'\w*\'\s*=\s*\'\w*\'.*\'\s*or\s*)',  # Multiple OR conditions
        r'(\"\s*or\s*\"\w*\"\s*=\s*\"\w*\".*\"\s*or\s*)',  # Multiple OR conditions for double quotes
    ]
    
    # Endpoints that should bypass strict validation
    SAFE_ENDPOINTS = [
        '/api/overtime/toggle',
        '/api/overtime/batch-toggle',
        '/api/staffs/add',
        '/api/staffs/remove'
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Request:
        """Process request through security validation."""
        
        # Check if this is a safe endpoint that should bypass strict validation
        is_safe_endpoint = any(request.url.path.startswith(endpoint) for endpoint in self.SAFE_ENDPOINTS)
        
        if is_safe_endpoint:
            logger.debug(f"Bypassing strict validation for safe endpoint: {request.url.path}")
        else:
            # Validate URL parameters
            self._validate_url_params(request)
            
            # Validate headers
            self._validate_headers(request)
        
        # For POST/PUT requests, validate body content
        if request.method in ["POST", "PUT", "PATCH"]:
            await self._validate_body(request, is_safe_endpoint)
        
        response = await call_next(request)
        return response
    
    def _validate_url_params(self, request: Request) -> None:
        """Validate URL parameters for dangerous content."""
        for param_name, param_value in request.query_params.items():
            if self._contains_dangerous_content(str(param_value)):
                logger.warning(f"Potentially dangerous content in URL parameter {param_name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected in parameters"
                )
    
    def _validate_headers(self, request: Request) -> None:
        """Validate headers for suspicious content."""
        suspicious_headers = ["user-agent", "referer", "cookie"]
        
        for header_name, header_value in request.headers.items():
            if header_name.lower() in suspicious_headers:
                if self._contains_dangerous_content(str(header_value)):
                    logger.warning(f"Suspicious content in header {header_name}")
                    # Don't block headers, just log them for monitoring
    
    async def _validate_body(self, request: Request, is_safe_endpoint: bool = False) -> None:
        """Validate request body for dangerous content."""
        try:
            # Get body content
            body = await request.body()
            
            if not body:
                return
            
            # Decode body for validation
            try:
                body_str = body.decode('utf-8')
            except UnicodeDecodeError:
                # Binary data, skip validation
                return
            
            # For safe endpoints, only check for obviously dangerous content
            if is_safe_endpoint:
                # Only check for script tags and obvious XSS attacks
                if self._contains_dangerous_content(body_str):
                    logger.warning(f"Potentially dangerous content in safe endpoint {request.url.path}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid input detected in request body"
                    )
                return
            
            # For other endpoints, apply full validation
            # Check for dangerous patterns
            if self._contains_dangerous_content(body_str):
                logger.warning(f"Potentially dangerous content in request body for {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected in request body"
                )
            
            # Check for SQL injection patterns
            if self._contains_sql_injection(body_str):
                logger.warning(f"Potential SQL injection attempt detected for {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        except Exception as e:
            # Log error but don't break the request unless it's a validation error
            logger.error(f"Error validating request body for {request.url.path}: {str(e)}")
            # Re-raise HTTPExceptions but let other exceptions pass
            if isinstance(e, HTTPException):
                raise
    
    def _contains_dangerous_content(self, content: str) -> bool:
        """Check if content contains potentially dangerous patterns."""
        content_lower = content.lower()
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_sql_injection(self, content: str) -> bool:
        """Check if content contains SQL injection patterns."""
        content_lower = content.lower()
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False

class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to add XSS protection headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Request:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add XSS protection headers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
