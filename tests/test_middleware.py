"""Tests for security middleware."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSecurityMiddleware:
    """Test security validation middleware."""
    
    def test_safe_request(self):
        """Test that safe requests pass through."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "version" in data
    
    def test_xss_protection_headers(self):
        """Test XSS protection headers are added."""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-XSS-Protection" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Referrer-Policy" in response.headers
    
    def test_malicious_url_params(self):
        """Test that malicious URL parameters are blocked."""
        # Test script tag in parameter
        response = client.get("/api/departments?test=<script>alert('xss')</script>")
        assert response.status_code == 400
        assert "Invalid input detected" in response.json()["detail"]
    
    def test_sql_injection_in_params(self):
        """Test that SQL injection attempts are blocked."""
        # Test SQL injection in parameter
        response = client.get("/api/departments?id=1' OR '1'='1")
        assert response.status_code == 400
        assert "Invalid input detected" in response.json()["detail"]
    
    def test_safe_params_pass(self):
        """Test that safe parameters pass through."""
        response = client.get("/api/departments?test=safe_parameter")
        # Should not be blocked by middleware (may fail for other reasons)
        assert response.status_code != 400

class TestAPIEndpoints:
    """Test that API endpoints work with middleware."""
    
    def test_departments_endpoint(self):
        """Test departments endpoint works."""
        response = client.get("/api/departments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_malicious_json_body(self):
        """Test that malicious JSON body is blocked."""
        malicious_data = {
            "name": "<script>alert('xss')</script>",
            "department_id": 1
        }
        
        response = client.post("/api/staffs/add", json=malicious_data)
        # Should be blocked by middleware
        assert response.status_code == 400
        assert "Invalid input detected" in response.json()["detail"]
    
    def test_safe_json_body(self):
        """Test that safe JSON body passes through."""
        safe_data = {
            "name": "Safe Name",
            "department_id": 1
        }
        
        response = client.post("/api/staffs/add", json=safe_data)
        # Should not be blocked by middleware (may fail for auth/other reasons)
        assert response.status_code != 400 or "Invalid input detected" not in response.json().get("detail", "")
