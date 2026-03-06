#!/usr/bin/env python3
"""
PackOptima AI - Complete Application Test Suite
Tests all backend endpoints and verifies frontend/backend integration
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.token = None
        self.user_email = f"test_{datetime.now().timestamp()}@example.com"
        self.product_id = None
        self.box_id = None
        self.run_id = None
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{text:^60}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    def print_test(self, name, passed, message=""):
        if passed:
            print(f"{GREEN}✓{RESET} {name}")
            self.passed += 1
        else:
            print(f"{RED}✗{RESET} {name}")
            if message:
                print(f"  {RED}Error: {message}{RESET}")
            self.failed += 1
            
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Test Summary{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALL TESTS PASSED! Application is working correctly.{RESET}\n")
            return 0
        else:
            print(f"\n{RED}❌ Some tests failed. Please check the errors above.{RESET}\n")
            return 1
    
    # Test 1: Backend Health Check
    def test_health_check(self):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            data = response.json()
            self.print_test(
                "Backend Health Check",
                response.status_code == 200 and data.get("status") == "healthy",
                f"Status: {response.status_code}, Response: {data}"
            )
        except Exception as e:
            self.print_test("Backend Health Check", False, str(e))
    
    # Test 2: Root Endpoint
    def test_root_endpoint(self):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            data = response.json()
            self.print_test(
                "Root Endpoint",
                response.status_code == 200 and "PackOptima AI API" in data.get("message", ""),
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Root Endpoint", False, str(e))
    
    # Test 3: User Registration
    def test_registration(self):
        try:
            payload = {
                "email": self.user_email,
                "password": "test12345",  # At least 8 characters
                "company_name": "Test Company"
            }
            response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "access_token" in data:
                self.token = data["access_token"]
                self.print_test("User Registration", True)
            else:
                self.print_test("User Registration", False, f"Status: {response.status_code}, Response: {data}")
        except Exception as e:
            self.print_test("User Registration", False, str(e))
    
    # Test 4: User Login
    def test_login(self):
        try:
            payload = {
                "email": self.user_email,
                "password": "test12345"  # At least 8 characters
            }
            response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "access_token" in data:
                self.token = data["access_token"]
                self.print_test("User Login", True)
            else:
                self.print_test("User Login", False, f"Status: {response.status_code}, Response: {data}")
        except Exception as e:
            self.print_test("User Login", False, str(e))
    
    # Test 5: Get Products (Empty)
    def test_get_products_empty(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Products (Empty)",
                response.status_code == 200 and isinstance(data, list) and len(data) == 0,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Products (Empty)", False, str(e))
    
    # Test 6: Create Product
    def test_create_product(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "sku": "TEST-001",
                "name": "Test Product",
                "length": 30.0,
                "width": 20.0,
                "height": 10.0,
                "weight": 2.5,
                "category": "Electronics",
                "current_box_cost": 5.0
            }
            response = requests.post(f"{BASE_URL}/products", json=payload, headers=headers, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "id" in data:
                self.product_id = data["id"]
                self.print_test("Create Product", True)
            else:
                self.print_test("Create Product", False, f"Status: {response.status_code}, Response: {data}")
        except Exception as e:
            self.print_test("Create Product", False, str(e))
    
    # Test 7: Get Products (With Data)
    def test_get_products_with_data(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Products (With Data)",
                response.status_code == 200 and isinstance(data, list) and len(data) == 1,
                f"Status: {response.status_code}, Count: {len(data) if isinstance(data, list) else 0}"
            )
        except Exception as e:
            self.print_test("Get Products (With Data)", False, str(e))
    
    # Test 8: Get Single Product
    def test_get_single_product(self):
        if not self.product_id:
            self.print_test("Get Single Product", False, "No product ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/products/{self.product_id}", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Single Product",
                response.status_code == 200 and data.get("id") == self.product_id,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Single Product", False, str(e))
    
    # Test 9: Update Product
    def test_update_product(self):
        if not self.product_id:
            self.print_test("Update Product", False, "No product ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": "Updated Test Product",
                "length": 35.0,
                "width": 25.0,
                "height": 15.0,
                "weight": 3.0,
                "category": "Electronics",
                "current_box_cost": 6.0
            }
            response = requests.put(f"{BASE_URL}/products/{self.product_id}", json=payload, headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Update Product",
                response.status_code == 200 and data.get("name") == "Updated Test Product",
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Update Product", False, str(e))
    
    # Test 10: Get Boxes (Empty)
    def test_get_boxes_empty(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/boxes", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Boxes (Empty)",
                response.status_code == 200 and isinstance(data, list) and len(data) == 0,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Boxes (Empty)", False, str(e))
    
    # Test 11: Create Box
    def test_create_box(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": "Test Box",
                "length": 40.0,
                "width": 30.0,
                "height": 20.0,
                "cost": 3.5
            }
            response = requests.post(f"{BASE_URL}/boxes", json=payload, headers=headers, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "id" in data:
                self.box_id = data["id"]
                self.print_test("Create Box", True)
            else:
                self.print_test("Create Box", False, f"Status: {response.status_code}, Response: {data}")
        except Exception as e:
            self.print_test("Create Box", False, str(e))
    
    # Test 12: Get Boxes (With Data)
    def test_get_boxes_with_data(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/boxes", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Boxes (With Data)",
                response.status_code == 200 and isinstance(data, list) and len(data) == 1,
                f"Status: {response.status_code}, Count: {len(data) if isinstance(data, list) else 0}"
            )
        except Exception as e:
            self.print_test("Get Boxes (With Data)", False, str(e))
    
    # Test 13: Run Optimization
    def test_run_optimization(self):
        if not self.product_id or not self.box_id:
            self.print_test("Run Optimization", False, "No product or box ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {"product_ids": None}  # Optimize all products
            response = requests.post(f"{BASE_URL}/optimize", json=payload, headers=headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and "run_id" in data:
                self.run_id = data["run_id"]
                self.print_test("Run Optimization", True)
            else:
                self.print_test("Run Optimization", False, f"Status: {response.status_code}, Response: {data}")
        except Exception as e:
            self.print_test("Run Optimization", False, str(e))
    
    # Test 14: Get Dashboard Analytics
    def test_get_dashboard(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Dashboard Analytics",
                response.status_code == 200 and "total_savings" in data,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Dashboard Analytics", False, str(e))
    
    # Test 15: Get Leakage Analysis
    def test_get_leakage(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/analytics/leakage", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Leakage Analysis",
                response.status_code == 200 and isinstance(data, list),
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Leakage Analysis", False, str(e))
    
    # Test 16: Get Inefficient Products
    def test_get_inefficient_products(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/analytics/inefficient", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Inefficient Products",
                response.status_code == 200 and isinstance(data, list),
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Inefficient Products", False, str(e))
    
    # Test 17: Get Savings Trends
    def test_get_trends(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/analytics/trends", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Savings Trends",
                response.status_code == 200 and isinstance(data, list),
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Savings Trends", False, str(e))
    
    # Test 18: Get Optimization History
    def test_get_history(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/history", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Optimization History",
                response.status_code == 200 and isinstance(data, list),
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Optimization History", False, str(e))
    
    # Test 19: Get Run Details
    def test_get_run_details(self):
        if not self.run_id:
            self.print_test("Get Run Details", False, "No run ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/history/{self.run_id}", headers=headers, timeout=5)
            data = response.json()
            
            self.print_test(
                "Get Run Details",
                response.status_code == 200 and "run" in data and "results" in data,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Get Run Details", False, str(e))
    
    # Test 20: Frontend Accessibility
    def test_frontend_accessible(self):
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            self.print_test(
                "Frontend Accessible",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Frontend Accessible", False, str(e))
    
    # Test 21: Delete Product
    def test_delete_product(self):
        if not self.product_id:
            self.print_test("Delete Product", False, "No product ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(f"{BASE_URL}/products/{self.product_id}", headers=headers, timeout=5)
            
            self.print_test(
                "Delete Product",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Delete Product", False, str(e))
    
    # Test 22: Delete Box
    def test_delete_box(self):
        if not self.box_id:
            self.print_test("Delete Box", False, "No box ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(f"{BASE_URL}/boxes/{self.box_id}", headers=headers, timeout=5)
            
            self.print_test(
                "Delete Box",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Delete Box", False, str(e))
    
    def run_all_tests(self):
        self.print_header("PackOptima AI - Complete Application Test")
        
        print(f"{YELLOW}Testing Backend API Endpoints...{RESET}\n")
        
        # Basic Tests
        self.print_header("Basic Connectivity Tests")
        self.test_health_check()
        self.test_root_endpoint()
        self.test_frontend_accessible()
        
        # Authentication Tests
        self.print_header("Authentication Tests")
        self.test_registration()
        self.test_login()
        
        # Product Tests
        self.print_header("Product Management Tests")
        self.test_get_products_empty()
        self.test_create_product()
        self.test_get_products_with_data()
        self.test_get_single_product()
        self.test_update_product()
        
        # Box Tests
        self.print_header("Box Management Tests")
        self.test_get_boxes_empty()
        self.test_create_box()
        self.test_get_boxes_with_data()
        
        # Optimization Tests
        self.print_header("Optimization Tests")
        self.test_run_optimization()
        
        # Analytics Tests
        self.print_header("Analytics Tests")
        self.test_get_dashboard()
        self.test_get_leakage()
        self.test_get_inefficient_products()
        self.test_get_trends()
        
        # History Tests
        self.print_header("History Tests")
        self.test_get_history()
        self.test_get_run_details()
        
        # Cleanup Tests
        self.print_header("Cleanup Tests")
        self.test_delete_product()
        self.test_delete_box()
        
        # Print Summary
        return self.print_summary()

if __name__ == "__main__":
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)
