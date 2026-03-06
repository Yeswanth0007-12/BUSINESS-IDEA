"""
Test script to verify both fixes:
1. Zero savings fix - auto-assign current boxes
2. Bulk upload fix - detailed error messages
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_zero_savings_fix():
    """Test that products without current_box_id now get auto-assigned and show savings"""
    print("\n" + "="*80)
    print("TEST 1: ZERO SAVINGS FIX - Auto-assign current boxes")
    print("="*80)
    
    # Register and login
    print("\n1. Registering test user...")
    register_data = {
        "email": f"test_savings_{int(time.time())}@test.com",
        "password": "testpass123",
        "company_name": "Test Savings Co"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.text}")
        return False
    
    print("✅ User registered")
    
    # Login
    print("\n2. Logging in...")
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in")
    
    # Create boxes
    print("\n3. Creating boxes...")
    boxes = [
        {"name": "Small Box", "length_cm": 20, "width_cm": 15, "height_cm": 10, "cost_per_unit": 1.0, "max_weight_kg": 5},
        {"name": "Medium Box", "length_cm": 30, "width_cm": 25, "height_cm": 20, "cost_per_unit": 2.0, "max_weight_kg": 10},
        {"name": "Large Box", "length_cm": 40, "width_cm": 35, "height_cm": 30, "cost_per_unit": 3.5, "max_weight_kg": 20},
        {"name": "XL Box", "length_cm": 50, "width_cm": 45, "height_cm": 40, "cost_per_unit": 5.0, "max_weight_kg": 30}
    ]
    
    for box in boxes:
        response = requests.post(f"{BASE_URL}/api/v1/boxes", json=box, headers=headers)
        if response.status_code != 201:
            print(f"❌ Failed to create box: {response.text}")
            return False
    
    print(f"✅ Created {len(boxes)} boxes")
    
    # Create products WITHOUT current_box_id
    print("\n4. Creating products WITHOUT current_box_id...")
    products = [
        {
            "name": "Test Product 1",
            "sku": "TEST-001",
            "category": "electronics",
            "length_cm": 15,
            "width_cm": 10,
            "height_cm": 8,
            "weight_kg": 2.0,
            "monthly_order_volume": 100,
            "current_box_id": None  # No current box assigned
        },
        {
            "name": "Test Product 2",
            "sku": "TEST-002",
            "category": "books",
            "length_cm": 25,
            "width_cm": 20,
            "height_cm": 15,
            "weight_kg": 5.0,
            "monthly_order_volume": 50,
            "current_box_id": None  # No current box assigned
        }
    ]
    
    for product in products:
        response = requests.post(f"{BASE_URL}/api/v1/products", json=product, headers=headers)
        if response.status_code != 201:
            print(f"❌ Failed to create product: {response.text}")
            return False
    
    print(f"✅ Created {len(products)} products WITHOUT current_box_id")
    
    # Run optimization
    print("\n5. Running optimization...")
    response = requests.post(f"{BASE_URL}/api/v1/optimization/optimize", json={}, headers=headers)
    if response.status_code != 200:
        print(f"❌ Optimization failed: {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Optimization completed")
    print(f"\nResults:")
    print(f"  Total products analyzed: {result['total_products_analyzed']}")
    print(f"  Products with savings: {result['products_with_savings']}")
    print(f"  Total monthly savings: ${result['total_monthly_savings']:.2f}")
    print(f"  Total annual savings: ${result['total_annual_savings']:.2f}")
    
    # Check individual results
    print(f"\n  Individual product results:")
    for res in result['results']:
        print(f"    - {res['product_name']}:")
        print(f"      Current box: {res['current_box_name']}")
        print(f"      Recommended box: {res['recommended_box_name']}")
        print(f"      Monthly savings: ${res['savings']:.2f}")
    
    # Verify fix: Products should now have current boxes assigned and show savings
    if result['total_monthly_savings'] > 0:
        print(f"\n✅ ZERO SAVINGS FIX VERIFIED: Products now show ${result['total_monthly_savings']:.2f} in savings!")
        return True
    else:
        print(f"\n⚠️  WARNING: Still showing $0 savings. Fix may not be working.")
        return False


def test_bulk_upload_error_messages():
    """Test that bulk upload shows detailed error messages for missing SKUs"""
    print("\n" + "="*80)
    print("TEST 2: BULK UPLOAD FIX - Detailed error messages")
    print("="*80)
    
    # Register and login
    print("\n1. Registering test user...")
    register_data = {
        "email": f"test_bulk_{int(time.time())}@test.com",
        "password": "testpass123",
        "company_name": "Test Bulk Co"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.text}")
        return False
    
    print("✅ User registered")
    
    # Login
    print("\n2. Logging in...")
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in")
    
    # Create only ONE product
    print("\n3. Creating ONE product...")
    product = {
        "name": "Existing Product",
        "sku": "EXIST-001",
        "category": "electronics",
        "length_cm": 15,
        "width_cm": 10,
        "height_cm": 8,
        "weight_kg": 2.0,
        "monthly_order_volume": 100
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/products", json=product, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create product: {response.text}")
        return False
    
    print(f"✅ Created product with SKU: {product['sku']}")
    
    # Create CSV with MISSING SKUs
    print("\n4. Creating CSV with MISSING SKUs...")
    csv_content = """order_number,customer_name,product_sku,quantity
ORD-001,John Doe,EXIST-001,2
ORD-002,Jane Smith,MISSING-001,1
ORD-003,Bob Johnson,MISSING-002,3
ORD-004,Alice Brown,MISSING-003,2"""
    
    # Upload CSV
    print("\n5. Uploading CSV with missing SKUs...")
    files = {"file": ("test_orders.csv", csv_content, "text/csv")}
    response = requests.post(f"{BASE_URL}/api/v1/bulk-upload", files=files, headers=headers)
    
    if response.status_code != 202:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    result = response.json()
    print(f"✅ Upload processed")
    print(f"\nResults:")
    print(f"  Total orders: {result['total_orders']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Message: {result['message']}")
    
    # Check for detailed error messages
    if 'failed_details' in result and len(result['failed_details']) > 0:
        print(f"\n✅ DETAILED ERROR MESSAGES FOUND:")
        for failure in result['failed_details']:
            print(f"\n  Order: {failure['order_number']}")
            print(f"  Error: {failure['error']}")
            if failure['missing_skus']:
                print(f"  Missing SKUs: {', '.join(failure['missing_skus'])}")
        
        print(f"\n✅ BULK UPLOAD FIX VERIFIED: Detailed error messages are now shown!")
        return True
    else:
        print(f"\n⚠️  WARNING: No detailed error messages found. Fix may not be working.")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING BOTH FIXES")
    print("="*80)
    
    # Test both fixes
    fix1_passed = test_zero_savings_fix()
    fix2_passed = test_bulk_upload_error_messages()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Fix 1 (Zero Savings): {'✅ PASSED' if fix1_passed else '❌ FAILED'}")
    print(f"Fix 2 (Bulk Upload): {'✅ PASSED' if fix2_passed else '❌ FAILED'}")
    
    if fix1_passed and fix2_passed:
        print(f"\n🎉 ALL FIXES VERIFIED AND WORKING!")
    else:
        print(f"\n⚠️  Some fixes may need additional work")
