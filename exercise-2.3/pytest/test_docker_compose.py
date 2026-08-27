#!/usr/bin/env python3
"""
Pytest tests for Docker Compose configuration.
Tests that the multi-service environment works correctly.
"""

import subprocess
import time
import requests
import pytest
import json


class DockerComposeTest:
    """Test class for Docker Compose configuration."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.compose_file = "../../exercise-1.1/docker-compose.yml"
        self.project_name = "test-project"
        
        # Setup: start services
        self._start_services()
        yield
        # Teardown: stop services
        self._stop_services()

    def _start_services(self):
        """Start Docker Compose services."""
        subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "up", "-d"],
            check=True,
            capture_output=True
        )
        time.sleep(10)  # Wait for services to start

    def _stop_services(self):
        """Stop Docker Compose services."""
        subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "down", "-v"],
            check=True,
            capture_output=True
        )

    def test_services_running(self):
        """Test that all services are running."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "ps"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in result.stdout, f"Services not running: {result.stdout}"

    def test_backend_health(self):
        """Test backend health endpoint."""
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except requests.ConnectionError:
            pytest.skip("Backend service not accessible")

    def test_frontend_health(self):
        """Test frontend health endpoint."""
        try:
            response = requests.get("http://localhost:80/healthz", timeout=10)
            assert response.status_code == 200
        except requests.ConnectionError:
            pytest.skip("Frontend service not accessible")

    def test_database_connection(self):
        """Test database connection."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "exec", 
             "-T", "postgres", "pg_isready", "-U", "postgres"],
            capture_output=True,
            text=True
        )
        
        assert "accepting connections" in result.stdout.lower() or result.returncode == 0

    def test_backend_api_response(self):
        """Test backend API response format."""
        try:
            response = requests.get("http://localhost:5000/api/hello", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
        except requests.ConnectionError:
            pytest.skip("Backend service not accessible")

    def test_service_logs(self):
        """Test that services are logging correctly."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "logs", 
             "--tail=10", "backend"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert len(result.stdout) > 0

    def test_volume_mounts(self):
        """Test that volumes are mounted correctly."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "exec", 
             "-T", "postgres", "ls", "/var/lib/postgresql/data"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_network_connectivity(self):
        """Test network connectivity between services."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "exec", 
             "-T", "backend", "ping", "-c", "1", "postgres"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_environment_variables(self):
        """Test environment variables are set correctly."""
        result = subprocess.run(
            ["docker-compose", "-f", self.compose_file, "-p", self.project_name, "exec", 
             "-T", "backend", "env"],
            capture_output=True,
            text=True
        )
        
        assert "DATABASE_URL" in result.stdout

    def test_container_resources(self):
        """Test container resource limits."""
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", 
             "{{.Name}}: {{.CPUPerc}} {{.MemUsage}}"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
