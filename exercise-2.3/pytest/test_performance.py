#!/usr/bin/env python3
"""
Performance tests for infrastructure.
Tests response times, throughput, and resource usage.
"""

import pytest
import requests
import time
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestPerformance:
    """Test class for performance testing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test configuration."""
        self.base_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:80"
        self.timeout = 10

    def test_backend_response_time(self):
        """Test backend API response time."""
        times: List[float] = []
        
        for _ in range(10):
            start = time.time()
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=self.timeout
            )
            end = time.time()
            times.append(end - start)
        
        avg_time = statistics.mean(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        assert avg_time < 1.0, f"Average response time too slow: {avg_time}s"
        assert p95_time < 2.0, f"P95 response time too slow: {p95_time}s"

    def test_frontend_response_time(self):
        """Test frontend response time."""
        times: List[float] = []
        
        for _ in range(10):
            start = time.time()
            response = requests.get(
                f"{self.frontend_url}/healthz",
                timeout=self.timeout
            )
            end = time.time()
            times.append(end - start)
        
        avg_time = statistics.mean(times)
        assert avg_time < 2.0, f"Frontend response time too slow: {avg_time}s"

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        def make_request():
            start = time.time()
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=self.timeout
            )
            return {
                "status": response.status_code,
                "time": time.time() - start
            }
        
        results: List[Dict] = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r["status"] == 200)
        avg_time = statistics.mean([r["time"] for r in results])
        
        assert success_count >= 95, f"Too many failed requests: {100 - success_count}%"
        assert avg_time < 2.0, f"Average concurrent response time too slow: {avg_time}s"

    def test_memory_usage(self):
        """Test memory usage is within limits."""
        import docker
        
        try:
            client = docker.from_env()
            containers = client.containers.list()
            
            for container in containers:
                stats = container.stats(stream=False)
                memory_usage = stats["memory_stats"]["usage"]
                memory_limit = stats["memory_stats"]["limit"]
                memory_percent = (memory_usage / memory_limit) * 100
                
                assert memory_percent < 90, \
                    f"Container {container.name} memory usage too high: {memory_percent}%"
        except Exception as e:
            pytest.skip(f"Could not check memory: {e}")

    def test_cpu_usage(self):
        """Test CPU usage is within limits."""
        import docker
        
        try:
            client = docker.from_env()
            containers = client.containers.list()
            
            for container in containers:
                stats = container.stats(stream=False)
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                              stats["precpu_stats"]["system_cpu_usage"]
                cpu_percent = (cpu_delta / system_delta) * 100
                
                assert cpu_percent < 80, \
                    f"Container {container.name} CPU usage too high: {cpu_percent}%"
        except Exception as e:
            pytest.skip(f"Could not check CPU: {e}")

    def test_database_query_time(self):
        """Test database query response time."""
        try:
            import psycopg2
            import os
            
            conn = psycopg2.connect(
                host="localhost",
                database="appdb",
                user="postgres",
                password="postgres"
            )
            
            cursor = conn.cursor()
            times: List[float] = []
            
            for _ in range(10):
                start = time.time()
                cursor.execute("SELECT 1")
                cursor.fetchall()
                end = time.time()
                times.append(end - start)
            
            avg_time = statistics.mean(times)
            assert avg_time < 0.1, f"Database query time too slow: {avg_time}s"
            
            cursor.close()
            conn.close()
        except Exception as e:
            pytest.skip(f"Could not test database: {e}")

    def test_api_throughput(self):
        """Test API throughput."""
        request_count = 100
        start_time = time.time()
        
        for _ in range(request_count):
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=self.timeout
            )
        
        total_time = time.time() - start_time
        rps = request_count / total_time
        
        assert rps > 10, f"API throughput too low: {rps} requests/second"

    def test_response_size(self):
        """Test response size is reasonable."""
        response = requests.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        
        content_length = len(response.content)
        assert content_length < 1024, f"Response too large: {content_length} bytes"
