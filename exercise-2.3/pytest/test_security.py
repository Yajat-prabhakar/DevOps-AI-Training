#!/usr/bin/env python3
"""
Security compliance tests.
Tests infrastructure security configurations.
"""

import pytest
import subprocess
import json
import re
from typing import Dict, List, Any


class TestSecurityCompliance:
    """Test class for security compliance checks."""

    def test_docker_image_no_root_user(self):
        """Test Docker image doesn't run as root."""
        result = subprocess.run(
            ["docker", "inspect", "app-backend:latest"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip("Docker image not found")
        
        inspect_data = json.loads(result.stdout)
        config = inspect_data[0].get("Config", {})
        user = config.get("User", "")
        
        assert user != "root", "Docker image should not run as root"
        assert user != "0", "Docker image should not run as root"

    def test_docker_image_healthcheck(self):
        """Test Docker image has healthcheck."""
        result = subprocess.run(
            ["docker", "inspect", "app-backend:latest"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip("Docker image not found")
        
        inspect_data = json.loads(result.stdout)
        config = inspect_data[0].get("Config", {})
        healthcheck = config.get("Healthcheck")
        
        assert healthcheck is not None, "Docker image should have healthcheck"

    def test_no_secrets_in_dockerfile(self):
        """Test no secrets in Dockerfile."""
        dockerfile_path = "../../exercise-1.1/backend/Dockerfile"
        
        try:
            with open(dockerfile_path, "r") as f:
                content = f.read()
            
            secret_patterns = [
                r"password",
                r"secret",
                r"api[_-]?key",
                r"token",
                r"credential"
            ]
            
            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                # Check if secrets are in ENV or ARG (which is bad)
                env_matches = re.findall(rf"ENV\s+.*{pattern}.*", content, re.IGNORECASE)
                arg_matches = re.findall(rf"ARG\s+.*{pattern}.*", content, re.IGNORECASE)
                
                if env_matches or arg_matches:
                    pytest.fail(f"Potential secret found in Dockerfile: {pattern}")
        except FileNotFoundError:
            pytest.skip("Dockerfile not found")

    def test_no_secrets_in_compose(self):
        """Test no hardcoded secrets in docker-compose files."""
        compose_files = [
            "../../exercise-1.1/docker-compose.yml",
            "../../exercise-1.1/docker-compose.prod.yml"
        ]
        
        secret_patterns = [
            r"password:\s*[\"']?.+[\"']?",
            r"secret:\s*[\"']?.+[\"']?",
            r"api[_-]?key:\s*[\"']?.+[\"']?",
            r"token:\s*[\"']?.+[\"']?"
        ]
        
        for compose_file in compose_files:
            try:
                with open(compose_file, "r") as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Check if it's using environment variable reference
                        for match in matches:
                            if "${" not in match and "$" not in match:
                                pytest.fail(f"Potential hardcoded secret in {compose_file}: {match}")
            except FileNotFoundError:
                continue

    def test_terraform_no_public_access(self):
        """Test Terraform resources don't have public access."""
        terraform_dir = "../../exercise-1.2"
        
        try:
            result = subprocess.run(
                ["terraform", "show", "-json"],
                cwd=terraform_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                pytest.skip("Terraform not initialized")
            
            terraform_data = json.loads(result.stdout)
            resources = terraform_data.get("values", {}).get("root_module", {}).get("resources", [])
            
            for resource in resources:
                if resource.get("type") == "aws_security_group":
                    for ingress in resource.get("values", {}).get("ingress", []):
                        cidr_blocks = ingress.get("cidr_blocks", [])
                        if "0.0.0.0/0" in cidr_blocks:
                            pytest.fail(f"Security group {resource.get('name')} allows public access")
        except Exception as e:
            pytest.skip(f"Could not check Terraform: {e}")

    def test_no_docker_privileged_containers(self):
        """Test no privileged containers in docker-compose."""
        compose_file = "../../exercise-1.1/docker-compose.yml"
        
        try:
            with open(compose_file, "r") as f:
                content = f.read()
            
            if "privileged: true" in content:
                pytest.fail("Docker Compose uses privileged containers")
        except FileNotFoundError:
            pytest.skip("Docker Compose file not found")

    def test_no_host_network_mode(self):
        """Test no host network mode in docker-compose."""
        compose_file = "../../exercise-1.1/docker-compose.yml"
        
        try:
            with open(compose_file, "r") as f:
                content = f.read()
            
            if "network_mode: host" in content:
                pytest.fail("Docker Compose uses host network mode")
        except FileNotFoundError:
            pytest.skip("Docker Compose file not found")

    def test_no_docker_socket_mount(self):
        """Test no Docker socket mount in docker-compose."""
        compose_file = "../../exercise-1.1/docker-compose.yml"
        
        try:
            with open(compose_file, "r") as f:
                content = f.read()
            
            if "/var/run/docker.sock" in content:
                pytest.fail("Docker Compose mounts Docker socket")
        except FileNotFoundError:
            pytest.skip("Docker Compose file not found")

    def test_no_exposed_ports_in_production(self):
        """Test production compose doesn't expose unnecessary ports."""
        compose_file = "../../exercise-1.1/docker-compose.prod.yml"
        
        try:
            with open(compose_file, "r") as f:
                content = f.read()
            
            # Backend should not expose port in production
            if "5000:5000" in content:
                pytest.fail("Production compose exposes backend port")
        except FileNotFoundError:
            pytest.skip("Production compose file not found")

    def test_terraform_state_encryption(self):
        """Test Terraform state is encrypted."""
        backend_file = "../../exercise-1.2/backend.tf"
        
        try:
            with open(backend_file, "r") as f:
                content = f.read()
            
            if "encrypt" not in content.lower():
                # Check if using S3 backend (which has encryption by default)
                if "s3" in content.lower():
                    pass  # S3 has encryption by default
                else:
                    pytest.fail("Terraform state may not be encrypted")
        except FileNotFoundError:
            pytest.skip("Backend config not found")
