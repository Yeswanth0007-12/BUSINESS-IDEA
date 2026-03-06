#!/usr/bin/env python3
"""
Final Comprehensive Test Suite - Tests all application features
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.total += 1
        self.passed += 1
        print_success(test_name)
    
    def add_fail(self, test_name, error):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, error))
        print_error(f"{test_name}: {error}")
    
    def print_summary(self):
        print_header("Test Summary")
        print(f"Total Tests: {self.total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        return self.failed == 0

def test_infrastructure():
    """Test infrastructure components"""
    print_header("1. Infrastructure Tests")
    results = TestResults()
    
    # Test backend health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            results.add_pass("Backend Health Check")
        else:
            results.add_fail("Backend Health Check", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Backend Health Check", str(e))
    
    # Test frontend accessibility
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            results.add_pass("Frontend Accessibility")
        else:
            results.add_fail("Frontend Accessibility", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Frontend Accessibility", str(e))
    
    # Test API docs
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            results.add_pass("API Documentation")
        else:
            results.add_fail("API Documentation", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("API Documentation", str(e))
    
    return results

def test_authentication():
    """Test authentication flow"""
    print_header("2. Authentication Tests")
    results = TestResults()
    
    # Generate unique email
    email = f"test_{int(time.time())}@packoptima.com"
    password = "TestPass123"
    company = "Test Company"
    
    # Test registration
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "company_name": company
        })
        if response.status_code == 201:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                results.add_pass("User Registration")
            else:
                results.add_fail("User Registration", "No access token returned")
        else:
            results.add_fail("User Registration", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("User Registration", str(e))
        return results
    
    # Test login
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                results.add_pass("User Login")
            else:
                results.add_fail("User Login", "No access token returned")
        else:
            results.add_fail("User Login", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("User Login", str(e))
        return results
    
    # Test protected endpoint
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            results.add_pass("Protected Endpoint Access")
        else:
            results.add_fail("Protected Endpoint Access", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Protected Endpoint Access", str(e))
    
    return results, access_token

def test_product_management(access_token):
    """Test product CRUD operations"""
    print_header("3. Product Management Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create product
    product_data = {
        "sku": f"TEST-{int(time.time())}",
        "name": "Test Product",
        "category": "Electronics",
        "length_cm": 30.0,
        "width_cm": 20.0,
        "height_cm": 10.0,
        "weight_kg": 2.5,
        "monthly_order_volume": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
        if response.status_code == 201:
            product = response.json()
            product_id = product.get("id")
            results.add_pass("Create Product")
        else:
            results.add_fail("Create Product", f"Status: {response.status_code}")
            return results, None
    except Exception as e:
        results.add_fail("Create Product", str(e))
        return results, None
    
    # Get products
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            products = response.json()
            if len(products) > 0:
                results.add_pass("Get Products")
            else:
                results.add_fail("Get Products", "No products returned")
        else:
            results.add_fail("Get Products", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Products", str(e))
    
    # Get single product
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}", headers=headers)
        if response.status_code == 200:
            results.add_pass("Get Single Product")
        else:
            results.add_fail("Get Single Product", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Single Product", str(e))
    
    # Update product
    try:
        update_data = {"name": "Updated Product"}
        response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            results.add_pass("Update Product")
        else:
            results.add_fail("Update Product", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Update Product", str(e))
    
    return results, product_id

def test_box_management(access_token):
    """Test box CRUD operations"""
    print_header("4. Box Management Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create box
    box_data = {
        "name": f"Test Box {int(time.time())}",
        "length_cm": 40.0,
        "width_cm": 30.0,
        "height_cm": 20.0,
        "cost_per_unit": 3.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/boxes", json=box_data, headers=headers)
        if response.status_code == 201:
            box = response.json()
            box_id = box.get("id")
            results.add_pass("Create Box")
        else:
            results.add_fail("Create Box", f"Status: {response.status_code}")
            return results, None
    except Exception as e:
        results.add_fail("Create Box", str(e))
        return results, None
    
    # Get boxes
    try:
        response = requests.get(f"{BASE_URL}/boxes", headers=headers)
        if response.status_code == 200:
            boxes = response.json()
            if len(boxes) > 0:
                results.add_pass("Get Boxes")
            else:
                results.add_fail("Get Boxes", "No boxes returned")
        else:
            results.add_fail("Get Boxes", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Boxes", str(e))
    
    # Get single box
    try:
        response = requests.get(f"{BASE_URL}/boxes/{box_id}", headers=headers)
        if response.status_code == 200:
            results.add_pass("Get Single Box")
        else:
            results.add_fail("Get Single Box", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get Single Box", str(e))
    
    return results, box_id

def test_optimization(access_token):
    """Test optimization engine"""
    print_header("5. Optimization Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Run optimization
    try:
        response = requests.post(f"{BASE_URL}/optimize", json={}, headers=headers)
        if response.status_code == 200:
            optimization = response.json()
            if "run_id" in optimization:
                results.add_pass("Run Optimization")
                run_id = optimization["run_id"]
            else:
                results.add_fail("Run Optimization", "No run_id in response")
                run_id = None
        else:
            results.add_fail("Run Optimization", f"Status: {response.status_code}")
            run_id = None
    except Exception as e:
        results.add_fail("Run Optimization", str(e))
        run_id = None
    
    return results, run_id

def test_analytics(access_token):
    """Test analytics endpoints"""
    print_header("6. Analytics Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Dashboard
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            results.add_pass("Dashboard Analytics")
        else:
            results.add_fail("Dashboard Analytics", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Dashboard Analytics", str(e))
    
    # Leakage
    try:
        response = requests.get(f"{BASE_URL}/analytics/leakage", headers=headers)
        if response.status_code == 200:
            results.add_pass("Leakage Analysis")
        else:
            results.add_fail("Leakage Analysis", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Leakage Analysis", str(e))
    
    # Inefficient products
    try:
        response = requests.get(f"{BASE_URL}/analytics/inefficient", headers=headers)
        if response.status_code == 200:
            results.add_pass("Inefficient Products")
        else:
            results.add_fail("Inefficient Products", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Inefficient Products", str(e))
    
    # Trends
    try:
        response = requests.get(f"{BASE_URL}/analytics/trends", headers=headers)
        if response.status_code == 200:
            results.add_pass("Savings Trends")
        else:
            results.add_fail("Savings Trends", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Savings Trends", str(e))
    
    return results

def test_history(access_token, run_id):
    """Test history endpoints"""
    print_header("7. History Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get history
    try:
        response = requests.get(f"{BASE_URL}/history", headers=headers)
        if response.status_code == 200:
            results.add_pass("Get History")
        else:
            results.add_fail("Get History", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Get History", str(e))
    
    # Get run details
    if run_id:
        try:
            response = requests.get(f"{BASE_URL}/history/{run_id}", headers=headers)
            if response.status_code == 200:
                results.add_pass("Get Run Details")
            else:
                results.add_fail("Get Run Details", f"Status: {response.status_code}")
        except Exception as e:
            results.add_fail("Get Run Details", str(e))
    
    return results

def test_cleanup(access_token, product_id, box_id):
    """Test delete operations"""
    print_header("8. Cleanup Tests")
    results = TestResults()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Delete product
    if product_id:
        try:
            response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
            if response.status_code == 204:
                results.add_pass("Delete Product")
            else:
                results.add_fail("Delete Product", f"Status: {response.status_code}")
        except Exception as e:
            results.add_fail("Delete Product", str(e))
    
    # Delete box
    if box_id:
        try:
            response = requests.delete(f"{BASE_URL}/boxes/{box_id}", headers=headers)
            if response.status_code == 204:
                results.add_pass("Delete Box")
            else:
                results.add_fail("Delete Box", f"Status: {response.status_code}")
        except Exception as e:
            results.add_fail("Delete Box", str(e))
    
    return results

def main():
    print_header("PackOptima AI - Final Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = []
    
    # Run all tests
    all_results.append(test_infrastructure())
    
    auth_results, access_token = test_authentication()
    all_results.append(auth_results)
    
    if access_token:
        product_results, product_id = test_product_management(access_token)
        all_results.append(product_results)
        
        box_results, box_id = test_box_management(access_token)
        all_results.append(box_results)
        
        opt_results, run_id = test_optimization(access_token)
        all_results.append(opt_results)
        
        all_results.append(test_analytics(access_token))
        all_results.append(test_history(access_token, run_id))
        all_results.append(test_cleanup(access_token, product_id, box_id))
    
    # Calculate totals
    total_tests = sum(r.total for r in all_results)
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    
    # Print final summary
    print_header("Final Results")
    print(f"Total Tests Run: {total_tests}")
    print(f"{Colors.GREEN}Total Passed: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}Total Failed: {total_failed}{Colors.RESET}")
    
    if total_failed == 0:
        print(f"\n{Colors.GREEN}{'='*70}")
        print("  ✓ ALL TESTS PASSED!")
        print(f"{'='*70}{Colors.RESET}\n")
        print("Your PackOptima AI application is fully operational!")
        return True
    else:
        print(f"\n{Colors.RED}{'='*70}")
        print(f"  ✗ {total_failed} TEST(S) FAILED")
        print(f"{'='*70}{Colors.RESET}\n")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
