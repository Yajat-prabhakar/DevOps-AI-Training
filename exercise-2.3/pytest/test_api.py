#!/usr/bin/env python3
"""
Pytest tests for API endpoints.
Tests the Flask backend API.
"""

import pytest
import requests
import json
from typing import Dict, Any


class TestBackendAPI:
    """Test class for backend API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test configuration."""
        self.base_url = "http://localhost:5000"
        self.timeout = 10

    def test_health_endpoint(self):
        """Test health endpoint returns 200."""
        response = requests.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        assert response.status_code == 200

    def test_health_response_format(self):
        """Test health endpoint response format."""
        response = requests.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_hello_endpoint(self):
        """Test hello endpoint returns 200."""
        response = requests.get(
            f"{self.base_url}/api/hello",
            timeout=self.timeout
        )
        assert response.status_code == 200

    def test_hello_response_format(self):
        """Test hello endpoint response format."""
        response = requests.get(
            f"{self.base_url}/api/hello",
            timeout=self.timeout
        )
        data = response.json()
        assert "message" in data

    def test_404_for_unknown_endpoint(self):
        """Test 404 for unknown endpoint."""
        response = requests.get(
            f"{self.base_url}/api/unknown",
            timeout=self.timeout
        )
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test 405 for wrong HTTP method."""
        response = requests.post(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        assert response.status_code == 405

    def test_response_time(self):
        """Test response time is within acceptable range."""
        start_time = requests.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        ).elapsed.total_seconds()
        
        assert start_time < 2.0, f"Response time too slow: {start_time}s"

    def test_content_type(self):
        """Test response content type is JSON."""
        response = requests.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        assert "application/json" in response.headers["Content-Type"]

    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = requests.options(
            f"{self.base_url}/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            },
            timeout=self.timeout
        )
        assert "Access-Control-Allow-Origin" in response.headers

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return requests.get(
                f"{self.base_url}/api/health",
                timeout=self.timeout
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        for response in results:
            assert response.status_code == 200
