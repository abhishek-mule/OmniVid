"""
Chaos engineering tests for OmniVid backend.
"""
import pytest
import time
import signal
import subprocess
import requests
import docker
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import random

# Configuration
TEST_TIMEOUT = 60  # seconds
SERVICE_HEALTH_CHECK_INTERVAL = 2  # seconds

def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return True
        except (requests.RequestException, ConnectionError):
            pass
        time.sleep(1)
    return False

class ChaosTestBase:
    """Base class for chaos tests."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class."""
        cls.docker_client = docker.from_env()
        
    def teardown_method(self, method):
        """Cleanup after each test."""
        # Ensure all containers are back up
        self._restart_services()
        
    def _get_service_container(self, service_name: str) -> Optional[docker.models.containers.Container]:
        """Get a service container by name."""
        try:
            return self.docker_client.containers.get(service_name)
        except docker.errors.NotFound:
            return None
            
    def _stop_service(self, service_name: str):
        """Stop a service container."""
        container = self._get_service_container(service_name)
        if container:
            container.stop(timeout=0)
            
    def _start_service(self, service_name: str):
        """Start a service container."""
        container = self._get_service_container(service_name)
        if container:
            container.start()
            
    def _restart_service(self, service_name: str):
        """Restart a service container."""
        container = self._get_service_container(service_name)
        if container:
            container.restart(timeout=0)
            
    def _restart_services(self):
        """Restart all services."""
        for service in ["omnivid-backend", "omnivid-db", "omnivid-redis", "omnivid-celery"]:
            self._start_service(service)
        
        # Wait for services to come back up
        assert wait_for_service("http://localhost:8000/health"), "Services did not recover after test"

class TestServiceResilience(ChaosTestBase):
    """Test service resilience to failures."""
    
    def test_database_failure(self):
        """Test that the system handles database failures gracefully."""
        # Stop the database
        self._stop_service("omnivid-db")
        
        # System should degrade gracefully
        try:
            response = requests.get("http://localhost:8000/api/videos", timeout=5)
            # Should either fail with a 503 or handle the error gracefully
            if response.status_code == 503:
                assert "database" in response.text.lower()
            else:
                assert response.status_code >= 400
        except requests.RequestException:
            # Connection error is also acceptable
            pass
            
        # Start the database again
        self._start_service("omnivid-db")
        
        # Wait for recovery
        assert wait_for_service("http://localhost:8000/health"), "Service did not recover after database restart"
        
    def test_redis_failure(self):
        """Test that the system handles Redis failures gracefully."""
        # Stop Redis
        self._stop_service("omnivid-redis")
        
        # System should degrade gracefully
        try:
            response = requests.get("http://localhost:8000/api/videos", timeout=5)
            # Should either work without cache or return an error
            assert response.status_code in (200, 503)
        except requests.RequestException:
            # Connection error is also acceptable
            pass
            
        # Start Redis again
        self._start_service("omnivid-redis")
        
        # Wait for recovery
        assert wait_for_service("http://localhost:8000/health"), "Service did not recover after Redis restart"
        
    def test_celery_worker_failure(self):
        """Test that the system handles Celery worker failures."""
        # Stop Celery workers
        self._stop_service("omnivid-celery")
        
        # Try to submit a video processing job
        response = requests.post(
            "http://localhost:8000/api/videos/process",
            json={"video_id": 1},
            timeout=5
        )
        
        # Should either queue the job or return an error
        assert response.status_code in (202, 503), "Unexpected response status code"
        
        # Start Celery workers again
        self._start_service("omnivid-celery")
        
        # Wait for recovery
        assert wait_for_service("http://localhost:8000/health"), "Service did not recover after Celery restart"

class TestNetworkPartition(ChaosTestBase):
    """Test network partition scenarios."""
    
    def _block_network(self, source: str, target: str):
        """Block network traffic between two services."""
        # This is a simplified example - in a real test, you would use tools like `tc` or `iptables`
        # to simulate network partitions
        pass
        
    def test_backend_database_partition(self):
        """Test network partition between backend and database."""
        # Simulate network partition (simplified)
        self._block_network("backend", "db")
        
        try:
            # The next request should fail or degrade gracefully
            response = requests.get("http://localhost:8000/api/videos", timeout=5)
            assert response.status_code >= 500 or response.status_code == 200
        except requests.RequestException:
            # Connection error is acceptable
            pass
            
    def test_backend_redis_partition(self):
        """Test network partition between backend and Redis."""
        # Simulate network partition (simplified)
        self._block_network("backend", "redis")
        
        try:
            # The next request should work without cache
            response = requests.get("http://localhost:8000/api/videos", timeout=5)
            assert response.status_code == 200
        except requests.RequestException:
            # Connection error is acceptable
            pass

class TestResourceExhaustion(ChaosTestBase):
    """Test system behavior under resource exhaustion."""
    
    def test_cpu_exhaustion(self):
        """Test system behavior under CPU pressure."""
        # Start a CPU-intensive process
        process = subprocess.Popen(
            ["stress", "--cpu", "4", "--timeout", "30s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # The system should remain responsive
            start_time = time.time()
            while time.time() - start_time < 20:  # Test for 20 seconds
                response = requests.get("http://localhost:8000/health", timeout=5)
                assert response.status_code == 200
                time.sleep(2)
        finally:
            process.terminate()
            
    def test_memory_exhaustion(self):
        """Test system behavior under memory pressure."""
        # Start a memory-intensive process
        process = subprocess.Popen(
            ["stress", "--vm", "2", "--vm-bytes", "1G", "--timeout", "30s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # The system should remain responsive or fail gracefully
            start_time = time.time()
            while time.time() - start_time < 20:  # Test for 20 seconds
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    assert response.status_code in (200, 503)
                except requests.RequestException:
                    # Connection errors are acceptable under memory pressure
                    pass
                time.sleep(2)
        finally:
            process.terminate()

class TestRecovery(ChaosTestBase):
    """Test system recovery after failures."""
    
    def test_service_restart(self):
        """Test that services recover after being restarted."""
        # Restart backend service
        self._restart_service("omnivid-backend")
        
        # Service should come back up
        assert wait_for_service("http://localhost:8000/health"), "Service did not recover after restart"
        
    def test_simultaneous_failures(self):
        """Test recovery from multiple simultaneous failures."""
        # Stop multiple services
        for service in ["omnivid-redis", "omnivid-db"]:
            self._stop_service(service)
            
        # Wait a bit
        time.sleep(5)
        
        # Start services again
        for service in ["omnivid-redis", "omnivid-db"]:
            self._start_service(service)
            
        # System should recover
        assert wait_for_service("http://localhost:8000/health"), "System did not recover from multiple failures"
