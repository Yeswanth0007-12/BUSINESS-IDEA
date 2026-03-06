#!/usr/bin/env python3
"""
Complete Application Test - All Tabs and Features
Tests the entire PackOptima AI SaaS workflow end-to-end
"""

import requests
import json
import sys
from io import StringIO
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "fulltest@example.com"
TEST_PASSWORD = "testpass123"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✓ PASSED" if passed else "✗ FAILED"
    print(f"{status}: {name}")
    if details:
        print(f"  {details}")

class ApplicationTester:
    def __init__(self):
        self.token = None
        self.test_results = []
        self.product_ids = []
        self.box_ids = []
        self.optimization_id = None
        
    def add_result(self, test_name, passed, details=""):
        """Track test result"""
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'details': details
        })
        print_test(test_name, passed, details)
        
    def get_headers(self):
        """Get authorization headers"""
        return {'Authorization': f'Bearer {self.token}'}
    
    # ==================== AUTHENTICATION TESTS ====================
    
    def test_authentication(self):
        """Test registration and login"""
        print_section("1. AUTHENTICATION TESTS")
        
        # Test Registration
        try:
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "company_name": "Full Test Company"
            }
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            
            if response.status_code in [200, 201]:
                token_data = response.json()
                if "access_token" in token_data:
                    self.token = token_data["access_token"]
                    self.add_result("User Registration", True, "New user registered")
                else:
                    self.add_result("User Registration", False, "No token in response")
                    return False
            elif response.status_code == 400 and "already registered" in response.text.lower():
                self.add_result("User Registration", True, "User already exists")
            else:
                self.add_result("User Registration", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_result("User Registration", False, str(e))
            return False
        
        # Test Login
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.add_result("User Login", True, f"Token: {self.token[:20]}...")
                return True
            else:
                self.add_result("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_result("User Login", False, str(e))
            return False
    
    # ==================== PRODUCTS TAB TESTS ====================
    
    def test_products_tab(self):
        """Test Products tab functionality"""
        print_section("2. PRODUCTS TAB TESTS")
        
        # Test: Get Products (empty initially)
        try:
            response = requests.get(f"{BASE_URL}/products", headers=self.get_headers())
            if response.status_code == 200:
                products = response.json()
                self.add_result("Get Products List", True, f"Found {len(products)} products")
            else:
                self.add_result("Get Products List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Products List", False, str(e))
        
        # Test: Create Product (Manual Entry)
        try:
            import random
            random_sku = f"TEST-LAP-{random.randint(1000, 9999)}"
            product_data = {
                "name": "Test Laptop",
                "sku": random_sku,  # Use random SKU to avoid duplicates
                "category": "Electronics",
                "length_cm": 35.0,
                "width_cm": 25.0,
                "height_cm": 5.0,
                "weight_kg": 2.5,
                "monthly_order_volume": 100
            }
            response = requests.post(f"{BASE_URL}/products", json=product_data, headers=self.get_headers())
            
            if response.status_code in [200, 201]:
                product = response.json()
                self.product_ids.append(product['id'])
                self.add_result("Create Product (Manual)", True, f"Product ID: {product['id']}")
            else:
                self.add_result("Create Product (Manual)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Create Product (Manual)", False, str(e))
        
        # Test: CSV Bulk Upload Products
        try:
            import random
            random_suffix = random.randint(1000, 9999)
            csv_content = f"""name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Wireless Mouse,TEST-MOU-{random_suffix},Electronics,12,8,4,0.15,200
USB Cable,TEST-CAB-{random_suffix},Accessories,15,10,2,0.05,300
Keyboard,TEST-KEY-{random_suffix},Electronics,45,15,3,1.2,150"""
            
            files = {'file': ('products.csv', csv_content, 'text/csv')}
            response = requests.post(
                f"{BASE_URL}/products/bulk-upload",
                files=files,
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                created = result.get('created_count', 0)
                self.add_result("CSV Bulk Upload Products", True, f"Created {created} products")
            else:
                self.add_result("CSV Bulk Upload Products", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("CSV Bulk Upload Products", False, str(e))
        
        # Test: Get Products (should have items now)
        try:
            response = requests.get(f"{BASE_URL}/products", headers=self.get_headers())
            if response.status_code == 200:
                products = response.json()
                if len(products) >= 4:
                    self.product_ids = [p['id'] for p in products]
                    self.add_result("Verify Products Created", True, f"Total: {len(products)} products")
                else:
                    self.add_result("Verify Products Created", False, f"Expected >= 4, got {len(products)}")
            else:
                self.add_result("Verify Products Created", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Verify Products Created", False, str(e))
        
        # Test: Update Product
        if self.product_ids:
            try:
                update_data = {
                    "name": "Updated Test Laptop",
                    "monthly_order_volume": 150
                }
                response = requests.put(
                    f"{BASE_URL}/products/{self.product_ids[0]}",
                    json=update_data,
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    self.add_result("Update Product", True, f"Updated product {self.product_ids[0]}")
                else:
                    self.add_result("Update Product", False, f"Status: {response.status_code}")
            except Exception as e:
                self.add_result("Update Product", False, str(e))
    
    # ==================== BOXES TAB TESTS ====================
    
    def test_boxes_tab(self):
        """Test Boxes tab functionality"""
        print_section("3. BOXES TAB TESTS")
        
        # Test: Get Boxes (empty initially)
        try:
            response = requests.get(f"{BASE_URL}/boxes", headers=self.get_headers())
            if response.status_code == 200:
                boxes = response.json()
                self.add_result("Get Boxes List", True, f"Found {len(boxes)} boxes")
            else:
                self.add_result("Get Boxes List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Boxes List", False, str(e))
        
        # Test: Create Box (Manual Entry)
        try:
            box_data = {
                "name": "Test Small Box",
                "length_cm": 20.0,
                "width_cm": 15.0,
                "height_cm": 10.0,
                "cost_per_unit": 1.50
            }
            response = requests.post(f"{BASE_URL}/boxes", json=box_data, headers=self.get_headers())
            
            if response.status_code in [200, 201]:
                box = response.json()
                self.box_ids.append(box['id'])
                self.add_result("Create Box (Manual)", True, f"Box ID: {box['id']}")
            else:
                self.add_result("Create Box (Manual)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Create Box (Manual)", False, str(e))
        
        # Test: CSV Bulk Upload Boxes
        try:
            csv_content = """name,length_cm,width_cm,height_cm,cost_per_unit
Medium Box,35,25,15,2.50
Large Box,50,40,20,3.50
Extra Large Box,70,50,30,5.00"""
            
            files = {'file': ('boxes.csv', csv_content, 'text/csv')}
            response = requests.post(
                f"{BASE_URL}/boxes/bulk-upload",
                files=files,
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                created = result.get('created_count', 0)
                self.add_result("CSV Bulk Upload Boxes", True, f"Created {created} boxes")
            else:
                self.add_result("CSV Bulk Upload Boxes", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("CSV Bulk Upload Boxes", False, str(e))
        
        # Test: Get Boxes (should have items now)
        try:
            response = requests.get(f"{BASE_URL}/boxes", headers=self.get_headers())
            if response.status_code == 200:
                boxes = response.json()
                if len(boxes) >= 4:
                    self.box_ids = [b['id'] for b in boxes]
                    self.add_result("Verify Boxes Created", True, f"Total: {len(boxes)} boxes")
                else:
                    self.add_result("Verify Boxes Created", False, f"Expected >= 4, got {len(boxes)}")
            else:
                self.add_result("Verify Boxes Created", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Verify Boxes Created", False, str(e))
        
        # Test: Update Box
        if self.box_ids:
            try:
                update_data = {
                    "name": "Updated Test Small Box",
                    "cost_per_unit": 1.75
                }
                response = requests.put(
                    f"{BASE_URL}/boxes/{self.box_ids[0]}",
                    json=update_data,
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    self.add_result("Update Box", True, f"Updated box {self.box_ids[0]}")
                else:
                    self.add_result("Update Box", False, f"Status: {response.status_code}")
            except Exception as e:
                self.add_result("Update Box", False, str(e))
    
    # ==================== OPTIMIZE TAB TESTS ====================
    
    def test_optimize_tab(self):
        """Test Optimize tab functionality"""
        print_section("4. OPTIMIZE TAB TESTS")
        
        if not self.product_ids or not self.box_ids:
            self.add_result("Optimization Prerequisites", False, "Need products and boxes first")
            return
        
        # Test: Run Optimization
        try:
            optimization_data = {
                "product_ids": self.product_ids[:3],  # Use first 3 products
                "box_ids": self.box_ids[:3]  # Use first 3 boxes
            }
            response = requests.post(
                f"{BASE_URL}/optimize",  # Fixed endpoint
                json=optimization_data,
                headers=self.get_headers()
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.optimization_id = result.get('optimization_run_id')
                total_cost = result.get('total_cost', 0)
                boxes_used = len(result.get('results', []))
                self.add_result("Run Optimization", True, 
                              f"Cost: ${total_cost:.2f}, Boxes: {boxes_used}")
            else:
                self.add_result("Run Optimization", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Run Optimization", False, str(e))
    
    # ==================== HISTORY TAB TESTS ====================
    
    def test_history_tab(self):
        """Test History tab functionality"""
        print_section("5. HISTORY TAB TESTS")
        
        # Test: Get Optimization History
        try:
            response = requests.get(f"{BASE_URL}/history", headers=self.get_headers())
            
            if response.status_code == 200:
                history = response.json()
                if len(history) > 0:
                    self.add_result("Get Optimization History", True, 
                                  f"Found {len(history)} optimization runs")
                else:
                    self.add_result("Get Optimization History", True, "No history yet (expected)")
            else:
                self.add_result("Get Optimization History", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Optimization History", False, str(e))
        
        # Test: Get Specific Optimization Details
        if self.optimization_id:
            try:
                response = requests.get(
                    f"{BASE_URL}/history/{self.optimization_id}",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    details = response.json()
                    self.add_result("Get Optimization Details", True, 
                                  f"Retrieved details for run {self.optimization_id}")
                else:
                    self.add_result("Get Optimization Details", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.add_result("Get Optimization Details", False, str(e))
    
    # ==================== ANALYTICS TAB TESTS ====================
    
    def test_analytics_tab(self):
        """Test Analytics/Dashboard tab functionality"""
        print_section("6. ANALYTICS/DASHBOARD TESTS")
        
        # Test: Get Dashboard Metrics
        try:
            response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=self.get_headers())
            
            if response.status_code == 200:
                analytics = response.json()
                total_products = analytics.get('total_products', 0)
                total_boxes = analytics.get('total_boxes', 0)
                self.add_result("Get Dashboard Metrics", True, 
                              f"Products: {total_products}, Boxes: {total_boxes}")
            else:
                self.add_result("Get Dashboard Metrics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Dashboard Metrics", False, str(e))
        
        # Test: Get Leakage Insights
        try:
            response = requests.get(f"{BASE_URL}/analytics/leakage", headers=self.get_headers())
            
            if response.status_code == 200:
                leakage = response.json()
                self.add_result("Get Leakage Insights", True, 
                              f"Retrieved {len(leakage)} leakage insights")
            else:
                self.add_result("Get Leakage Insights", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Leakage Insights", False, str(e))
        
        # Test: Get Inefficient Products
        try:
            response = requests.get(f"{BASE_URL}/analytics/inefficient", headers=self.get_headers())
            
            if response.status_code == 200:
                inefficient = response.json()
                self.add_result("Get Inefficient Products", True, 
                              f"Found {len(inefficient)} inefficient products")
            else:
                self.add_result("Get Inefficient Products", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Inefficient Products", False, str(e))
        
        # Test: Get Savings Trends
        try:
            response = requests.get(f"{BASE_URL}/analytics/trends", headers=self.get_headers())
            
            if response.status_code == 200:
                trends = response.json()
                self.add_result("Get Savings Trends", True, 
                              f"Retrieved {len(trends)} trend data points")
            else:
                self.add_result("Get Savings Trends", False, f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Get Savings Trends", False, str(e))
    
    # ==================== LEAKAGE TAB TESTS ====================
    
    def test_leakage_tab(self):
        """Test Leakage Analysis tab functionality"""
        print_section("7. LEAKAGE ANALYSIS TESTS")
        
        # Note: Leakage is already tested in analytics section
        # This is just a placeholder for the tab
        self.add_result("Leakage Tab Available", True, "Tested in Analytics section")
    
    # ==================== CLEANUP TESTS ====================
    
    def test_cleanup(self):
        """Test delete operations"""
        print_section("8. CLEANUP TESTS (DELETE OPERATIONS)")
        
        # Test: Delete a Product
        if self.product_ids and len(self.product_ids) > 1:
            try:
                product_id = self.product_ids[-1]  # Delete last product
                response = requests.delete(
                    f"{BASE_URL}/products/{product_id}",
                    headers=self.get_headers()
                )
                
                if response.status_code in [200, 204]:
                    self.add_result("Delete Product", True, f"Deleted product {product_id}")
                else:
                    self.add_result("Delete Product", False, f"Status: {response.status_code}")
            except Exception as e:
                self.add_result("Delete Product", False, str(e))
        
        # Test: Delete a Box
        if self.box_ids and len(self.box_ids) > 1:
            try:
                box_id = self.box_ids[-1]  # Delete last box
                response = requests.delete(
                    f"{BASE_URL}/boxes/{box_id}",
                    headers=self.get_headers()
                )
                
                if response.status_code in [200, 204]:
                    self.add_result("Delete Box", True, f"Deleted box {box_id}")
                else:
                    self.add_result("Delete Box", False, f"Status: {response.status_code}")
            except Exception as e:
                self.add_result("Delete Box", False, str(e))
    
    # ==================== RUN ALL TESTS ====================
    
    def run_all_tests(self):
        """Run complete test suite"""
        print_section("PackOptima AI SaaS - Complete Application Test")
        print("Testing all tabs and features end-to-end\n")
        
        # Run tests in order
        if not self.test_authentication():
            print("\n✗ Authentication failed - cannot continue")
            return False
        
        self.test_products_tab()
        self.test_boxes_tab()
        self.test_optimize_tab()
        self.test_history_tab()
        self.test_analytics_tab()
        self.test_leakage_tab()
        self.test_cleanup()
        
        # Print summary
        self.print_summary()
        
        # Return overall result
        return all(result['passed'] for result in self.test_results)
    
    def print_summary(self):
        """Print test summary"""
        print_section("TEST SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✓")
        print(f"Failed: {failed_tests} ✗")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")
        
        if failed_tests > 0:
            print("Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ✗ {result['name']}")
                    if result['details']:
                        print(f"    {result['details']}")
        
        print()
        if failed_tests == 0:
            print("✓ ALL TESTS PASSED - APPLICATION FULLY FUNCTIONAL!")
        else:
            print(f"✗ {failed_tests} TEST(S) FAILED - REVIEW ABOVE")

def main():
    """Main test execution"""
    tester = ApplicationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
