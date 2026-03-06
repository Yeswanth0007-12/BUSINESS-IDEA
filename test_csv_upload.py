#!/usr/bin/env python3
"""
Comprehensive CSV Upload Test for PackOptima AI SaaS
Tests both Products and Boxes CSV upload functionality
"""

import requests
import json
import sys
from io import StringIO

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "csvtest@example.com"
TEST_PASSWORD = "testpass123"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def register_and_login():
    """Register a new user and login to get access token"""
    print_section("AUTHENTICATION")
    
    # Register
    print("Registering test user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "company_name": "CSV Test Company"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201]:
            print("✓ User registered successfully")
            # If registration returns a token, use it directly
            if response.status_code == 201:
                token_data = response.json()
                if "access_token" in token_data:
                    access_token = token_data.get("access_token")
                    print(f"✓ Token received from registration")
                    print(f"  Token: {access_token[:20]}...")
                    return access_token
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print("✓ User already exists, proceeding to login")
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Registration error: {e}")
    
    # Login
    print("Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✓ Login successful")
            print(f"  Token: {access_token[:20]}...")
            return access_token
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_products_csv_upload(token):
    """Test Products CSV bulk upload"""
    print_section("PRODUCTS CSV UPLOAD TEST")
    
    # Create CSV content
    csv_content = """name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Laptop Computer,LAP-001,Electronics,35,25,5,2.5,150
Wireless Mouse,MOU-001,Electronics,12,8,4,0.15,300
USB Cable,CAB-001,Accessories,15,10,2,0.05,500
Monitor 24inch,MON-001,Electronics,60,45,10,5.5,80
Keyboard Mechanical,KEY-001,Electronics,45,15,3,1.2,120"""
    
    print("CSV Content:")
    print(csv_content)
    print()
    
    # Prepare file upload
    files = {
        'file': ('products.csv', csv_content, 'text/csv')
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        print("Uploading products CSV...")
        response = requests.post(
            f"{BASE_URL}/products/bulk-upload",
            files=files,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Created: {result.get('created_count', 0)} products")
            errors = result.get('errors', []) or []
            print(f"  Errors: {len(errors)} errors")
            
            if errors:
                print("\n  Error details:")
                for error in errors:
                    if isinstance(error, dict):
                        print(f"    - Row {error.get('row', '?')}: {error.get('error', 'Unknown error')}")
                    else:
                        print(f"    - {error}")
            
            return True
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False

def test_boxes_csv_upload(token):
    """Test Boxes CSV bulk upload"""
    print_section("BOXES CSV UPLOAD TEST")
    
    # Create CSV content
    csv_content = """name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
Medium Box,35,25,15,2.50
Large Box,50,40,20,3.50
Extra Large Box,70,50,30,5.00
Envelope,30,20,2,0.75"""
    
    print("CSV Content:")
    print(csv_content)
    print()
    
    # Prepare file upload
    files = {
        'file': ('boxes.csv', csv_content, 'text/csv')
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        print("Uploading boxes CSV...")
        response = requests.post(
            f"{BASE_URL}/boxes/bulk-upload",
            files=files,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✓ Upload successful!")
            print(f"  Created: {result.get('created_count', 0)} boxes")
            errors = result.get('errors', []) or []
            print(f"  Errors: {len(errors)} errors")
            
            if errors:
                print("\n  Error details:")
                for error in errors:
                    if isinstance(error, dict):
                        print(f"    - Row {error.get('row', '?')}: {error.get('error', 'Unknown error')}")
                    else:
                        print(f"    - {error}")
            
            return True
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False

def verify_data(token):
    """Verify uploaded data"""
    print_section("DATA VERIFICATION")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Check products
    print("Checking products...")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            products = response.json()
            print(f"✓ Found {len(products)} products")
            if products:
                print(f"  Sample: {products[0].get('name', 'N/A')} - SKU: {products[0].get('sku', 'N/A')}")
        else:
            print(f"✗ Failed to fetch products: {response.status_code}")
    except Exception as e:
        print(f"✗ Error fetching products: {e}")
    
    # Check boxes
    print("\nChecking boxes...")
    try:
        response = requests.get(f"{BASE_URL}/boxes", headers=headers)
        if response.status_code == 200:
            boxes = response.json()
            print(f"✓ Found {len(boxes)} boxes")
            if boxes:
                print(f"  Sample: {boxes[0].get('name', 'N/A')} - Cost: ${boxes[0].get('cost_per_unit', 0):.2f}")
        else:
            print(f"✗ Failed to fetch boxes: {response.status_code}")
    except Exception as e:
        print(f"✗ Error fetching boxes: {e}")

def main():
    """Main test execution"""
    print_section("PackOptima CSV Upload Test Suite")
    print("Testing Products and Boxes CSV bulk upload functionality")
    
    # Step 1: Authenticate
    token = register_and_login()
    if not token:
        print("\n✗ FAILED: Could not authenticate")
        sys.exit(1)
    
    # Step 2: Test Products CSV Upload
    products_success = test_products_csv_upload(token)
    
    # Step 3: Test Boxes CSV Upload
    boxes_success = test_boxes_csv_upload(token)
    
    # Step 4: Verify Data
    verify_data(token)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"Products CSV Upload: {'✓ PASSED' if products_success else '✗ FAILED'}")
    print(f"Boxes CSV Upload: {'✓ PASSED' if boxes_success else '✗ FAILED'}")
    
    if products_success and boxes_success:
        print("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
