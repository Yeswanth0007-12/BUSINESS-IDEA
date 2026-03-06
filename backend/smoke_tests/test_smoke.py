"""
Smoke tests for PackOptima post-deployment verification.
Quick tests to verify critical functionality is working.
"""

import pytest
import requests
import time
from typing import Dict


# Configuration
BASE_URL = "http://localhost:8000"  # Override with environment variable
TEST_EMAIL = "smoke_test@example.com"
TEST_PASSWORD = "smoke_test_password_123"


@pytest.mark.smoke
class TestHealthChecks:
    """Smoke tests for health check endpoints"""
    
    def test_health_endpoint_responds(self):
        """Test that /health endpoint responds"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        assert response.status_code == 200, "Health endpoint should return 200"
        assert response.json().get("status") == "healthy", "Status should be healthy"
    
    def test_database_connectivity(self):
        """Test that database is accessible"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        health_data = response.json()
        assert "database" in health_data, "Health check should include database status"
        assert health_data["database"] == "connected", "Database should be connected"
    
    def test_redis_connectivity(self):
        """Test that Redis is accessible"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        health_data = response.json()
        assert "redis" in health_data, "Health check should include Redis status"
        assert health_data["redis"] == "connected", "Redis should be connected"
    
    def test_celery_workers_running(self):
        """Test that Celery workers are running"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        health_data = response.json()
        assert "celery_workers" in health_data, "Health check should include Celery status"
        assert health_data["celery_workers"] > 0, "At least one Celery worker should be running"


@pytest.mark.smoke
class TestAuthenticationEndpoints:
    """Smoke tests for authentication endpoints"""
    
    def test_login_endpoint_responds(self):
        """Test that login endpoint responds"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=5
        )
        
        # Should return 200 (success) or 401 (invalid credentials)
        assert response.status_code in [200, 401], "Login endpoint should respond"
    
    def test_register_endpoint_responds(self):
        """Test that register endpoint responds"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": f"test_{int(time.time())}@example.com",
                "password": "test_password_123",
                "company_name": "Test Company"
            },
            timeout=5
        )
        
        # Should return 201 (created) or 400 (validation error)
        assert response.status_code in [201, 400], "Register endpoint should respond"


@pytest.mark.smoke
class TestCoreEndpoints:
    """Smoke tests for core API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self) -> str:
        """Get authentication token for tests"""
        # Try to login with test user
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        
        # If login fails, try to register
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "company_name": "Smoke Test Company"
            }
        )
        
        if response.status_code == 201:
            # Login again
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            return response.json()["access_token"]
        
        pytest.skip("Could not authenticate for smoke tests")
    
    def test_products_endpoint_responds(self, auth_token):
        """Test that products endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/products", headers=headers, timeout=5)
        
        assert response.status_code == 200, "Products endpoint should return 200"
        assert isinstance(response.json(), list), "Products should return a list"
    
    def test_boxes_endpoint_responds(self, auth_token):
        """Test that boxes endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/boxes", headers=headers, timeout=5)
        
        assert response.status_code == 200, "Boxes endpoint should return 200"
        assert isinstance(response.json(), list), "Boxes should return a list"
    
    def test_optimization_endpoint_responds(self, auth_token):
        """Test that optimization endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # This might fail if no products exist, but should respond
        response = requests.post(
            f"{BASE_URL}/api/v1/optimize",
            json={"product_id": 1},
            headers=headers,
            timeout=5
        )
        
        # Should return 200 (success) or 404 (product not found) or 400 (validation error)
        assert response.status_code in [200, 400, 404], "Optimization endpoint should respond"
    
    def test_analytics_endpoint_responds(self, auth_token):
        """Test that analytics endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/summary",
            headers=headers,
            timeout=5
        )
        
        assert response.status_code == 200, "Analytics endpoint should return 200"
        assert isinstance(response.json(), dict), "Analytics should return a dict"


@pytest.mark.smoke
class TestAsyncEndpoints:
    """Smoke tests for async/queue endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self) -> str:
        """Get authentication token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        
        pytest.skip("Could not authenticate for smoke tests")
    
    def test_async_optimization_endpoint_responds(self, auth_token):
        """Test that async optimization endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/optimize/async",
            json={"product_id": 1},
            headers=headers,
            timeout=5
        )
        
        # Should return 202 (accepted) or 400/404 (validation/not found)
        assert response.status_code in [202, 400, 404], "Async optimization should respond"
    
    def test_task_status_endpoint_responds(self, auth_token):
        """Test that task status endpoint responds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try with a dummy task ID
        response = requests.get(
            f"{BASE_URL}/api/v1/tasks/dummy-task-id",
            headers=headers,
            timeout=5
        )
        
        # Should return 404 (not found) or 200 (found)
        assert response.status_code in [200, 404], "Task status endpoint should respond"


@pytest.mark.smoke
class TestResponseTimes:
    """Smoke tests for response time performance"""
    
    @pytest.fixture(scope="class")
    def auth_token(self) -> str:
        """Get authentication token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        
        pytest.skip("Could not authenticate for smoke tests")
    
    def test_health_check_responds_quickly(self):
        """Test that health check responds in < 1 second"""
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check took {elapsed:.2f}s, should be < 1s"
    
    def test_products_list_responds_quickly(self, auth_token):
        """Test that products list responds in < 2 seconds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/products", headers=headers, timeout=5)
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Products list took {elapsed:.2f}s, should be < 2s"
    
    def test_analytics_responds_quickly(self, auth_token):
        """Test that analytics responds in < 2 seconds"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/summary",
            headers=headers,
            timeout=5
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Analytics took {elapsed:.2f}s, should be < 2s"


@pytest.mark.smoke
class TestErrorHandling:
    """Smoke tests for error handling"""
    
    def test_invalid_endpoint_returns_404(self):
        """Test that invalid endpoints return 404"""
        response = requests.get(f"{BASE_URL}/api/v1/invalid-endpoint", timeout=5)
        
        assert response.status_code == 404, "Invalid endpoint should return 404"
    
    def test_unauthorized_request_returns_401(self):
        """Test that unauthorized requests return 401"""
        response = requests.get(f"{BASE_URL}/api/v1/products", timeout=5)
        
        assert response.status_code == 401, "Unauthorized request should return 401"
    
    def test_invalid_json_returns_400(self):
        """Test that invalid JSON returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        assert response.status_code in [400, 422], "Invalid JSON should return 400 or 422"


def run_smoke_tests():
    """Run all smoke tests and return results"""
    print("=" * 60)
    print("Running PackOptima Smoke Tests")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print()
    
    # Run tests
    exit_code = pytest.main([
        __file__,
        "-v",
        "-m", "smoke",
        "--tb=short",
        "--color=yes"
    ])
    
    print()
    print("=" * 60)
    if exit_code == 0:
        print("✓ All smoke tests passed")
    else:
        print("✗ Some smoke tests failed")
    print("=" * 60)
    
    return exit_code


if __name__ == '__main__':
    import sys
    sys.exit(run_smoke_tests())
