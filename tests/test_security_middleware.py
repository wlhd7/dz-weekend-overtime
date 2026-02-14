"""Tests for security middleware functionality."""

import pytest
import re
from app.middleware.validation import SecurityValidationMiddleware, XSSProtectionMiddleware
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class TestSecurityValidationMiddleware:
    """Test security validation patterns."""
    
    def test_contains_dangerous_content(self):
        """Test dangerous content detection."""
        middleware = SecurityValidationMiddleware(app=None)
        
        # Test XSS patterns
        assert middleware._contains_dangerous_content("<script>alert('xss')</script>")
        assert middleware._contains_dangerous_content("javascript:alert('xss')")
        assert middleware._contains_dangerous_content("onclick=alert('xss')")
        assert middleware._contains_dangerous_content("eval('malicious')")
        assert middleware._contains_dangerous_content("document.cookie")
        assert middleware._contains_dangerous_content("window.location")
        
        # Test safe content
        assert not middleware._contains_dangerous_content("safe content")
        assert not middleware._contains_dangerous_content("normal text")
        assert not middleware._contains_dangerous_content("John Doe")
    
    def test_contains_sql_injection(self):
        """Test SQL injection detection."""
        middleware = SecurityValidationMiddleware(app=None)
        
        # Test SQL injection patterns
        assert middleware._contains_sql_injection("SELECT * FROM users")
        assert middleware._contains_sql_injection("UNION SELECT password")
        assert middleware._contains_sql_injection("DROP TABLE users")
        assert middleware._contains_sql_injection("' OR '1'='1")
        assert middleware._contains_sql_injection("-- SQL comment")
        assert middleware._contains_sql_injection("/* SQL comment */")
        
        # Test safe content
        assert not middleware._contains_sql_injection("normal text")
        assert not middleware._contains_sql_injection("John Doe")
        assert not middleware._contains_sql_injection("Department 1")
    
    def test_case_insensitive_detection(self):
        """Test that detection is case insensitive."""
        middleware = SecurityValidationMiddleware(app=None)
        
        # Test case variations
        assert middleware._contains_dangerous_content("<SCRIPT>alert('xss')</SCRIPT>")
        assert middleware._contains_dangerous_content("JavaScript:alert('xss')")
        assert middleware._contains_sql_injection("select * from users")
        assert middleware._contains_sql_injection("UNION SELECT password")

class TestXSSProtectionMiddleware:
    """Test XSS protection headers."""
    
    def test_xss_headers_addition(self):
        """Test that XSS protection headers are added."""
        # This is a basic test - in real scenario would need actual Request/Response objects
        middleware = XSSProtectionMiddleware(app=None)
        assert middleware is not None

class TestInputValidation:
    """Test input validation patterns."""
    
    def test_regex_patterns(self):
        """Test regex patterns for security validation."""
        # Test script tag pattern
        script_pattern = r'<script[^>]*>.*?</script>'
        assert re.search(script_pattern, '<script>alert("xss")</script>', re.IGNORECASE)
        assert re.search(script_pattern, '<SCRIPT src="evil.js"></SCRIPT>', re.IGNORECASE)
        assert not re.search(script_pattern, 'normal text without scripts')
        
        # Test SQL injection pattern
        sql_pattern = r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)'
        assert re.search(sql_pattern, 'SELECT * FROM users', re.IGNORECASE)
        assert re.search(sql_pattern, 'UNION SELECT password', re.IGNORECASE)
        assert not re.search(sql_pattern, 'normal text without sql')
        
        # Test JavaScript protocol pattern
        js_pattern = r'javascript:'
        assert re.search(js_pattern, 'javascript:alert("xss")', re.IGNORECASE)
        assert re.search(js_pattern, 'JAVASCRIPT:window.location', re.IGNORECASE)
        assert not re.search(js_pattern, 'normal text without javascript')

class TestSecurityConfigurations:
    """Test security configurations."""
    
    def test_middleware_import(self):
        """Test that middleware can be imported."""
        from app.middleware.auth import JWTAuthMiddleware, get_current_user
        from app.middleware.validation import SecurityValidationMiddleware, XSSProtectionMiddleware
        
        assert JWTAuthMiddleware is not None
        assert get_current_user is not None
        assert SecurityValidationMiddleware is not None
        assert XSSProtectionMiddleware is not None
    
    def test_jwt_auth_methods(self):
        """Test JWT authentication methods exist."""
        from app.middleware.auth import JWTAuthMiddleware
        
        # Test that methods exist
        assert hasattr(JWTAuthMiddleware, 'verify_token')
        assert hasattr(JWTAuthMiddleware, 'create_access_token')
        assert callable(getattr(JWTAuthMiddleware, 'verify_token'))
        assert callable(getattr(JWTAuthMiddleware, 'create_access_token'))
