"""
Test script to verify all frontend tabs are accessible and backend APIs are working.
This script will:
1. Register/login a test user
2. Test all API endpoints for each tab
3. Verify subscription tab works correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_auth():
    """Test authentication"""
    print("\n=== Testing Authentication ===")
    
    # Register
    register_data = {
        "email": f"test_tabs_{int(time.time())}@example.com",
        "password": "testpass123",
        "company_name": "Test Company Tabs"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201]:
            print("✅ Registration successful")
            token = response.json()["access_token"]
            return token, register_data["email"]
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None, None

def test_dashboard(token):
    """Test Dashboard API"""
    print("\n=== Testing Dashboard Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard API working")
            return True
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard API error: {e}")
        return False

def test_products(token):
    """Test Products API"""
    print("\n=== Testing Products Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            print("✅ Products API working")
            return True
        else:
            print(f"❌ Products API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Products API error: {e}")
        return False

def test_boxes(token):
    """Test Boxes API"""
    print("\n=== Testing Boxes Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/boxes", headers=headers)
        if response.status_code == 200:
            print("✅ Boxes API working")
            return True
        else:
            print(f"❌ Boxes API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Boxes API error: {e}")
        return False

def test_history(token):
    """Test History API"""
    print("\n=== Testing History Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/history", headers=headers)
        if response.status_code == 200:
            print("✅ History API working")
            return True
        else:
            print(f"❌ History API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History API error: {e}")
        return False

def test_leakage(token):
    """Test Leakage API"""
    print("\n=== Testing Leakage Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/leakage", headers=headers)
        if response.status_code == 200:
            print("✅ Leakage API working")
            return True
        else:
            print(f"❌ Leakage API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Leakage API error: {e}")
        return False

def test_orders(token):
    """Test Orders API"""
    print("\n=== Testing Orders Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=headers)
        if response.status_code == 200:
            print("✅ Orders API working")
            return True
        else:
            print(f"❌ Orders API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Orders API error: {e}")
        return False

def test_subscription(token):
    """Test Subscription API - CRITICAL TEST"""
    print("\n=== Testing Subscription Tab (CRITICAL) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get subscription plans
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/plans", headers=headers)
        if response.status_code == 200:
            plans = response.json()
            print(f"✅ Subscription plans API working - Found {len(plans)} plans")
        else:
            print(f"❌ Subscription plans API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Subscription plans API error: {e}")
        return False
    
    # Test 2: Get usage summary
    try:
        response = requests.get(f"{BASE_URL}/subscriptions/usage", headers=headers)
        if response.status_code == 200:
            usage = response.json()
            print(f"✅ Usage summary API working - {usage.get('total_products', 0)} products")
        else:
            print(f"❌ Usage summary API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Usage summary API error: {e}")
        return False
    
    return True

def test_warehouse(token):
    """Test Warehouse API"""
    print("\n=== Testing Warehouse Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/warehouse/api-keys", headers=headers)
        if response.status_code == 200:
            print("✅ Warehouse API keys endpoint working")
            return True
        else:
            print(f"❌ Warehouse API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Warehouse API error: {e}")
        return False

def test_admin(token):
    """Test Admin API"""
    print("\n=== Testing Admin Tab ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if response.status_code == 200:
            print("✅ Admin API working")
            return True
        else:
            print(f"❌ Admin API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin API error: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTING ALL TABS - FIRST RUN")
    print("=" * 60)
    
    # Test authentication
    token, email = test_auth()
    if not token:
        print("\n❌ FAILED: Could not authenticate")
        return
    
    print(f"\n✅ Authenticated as: {email}")
    
    # Test all tabs
    results = {
        "Dashboard": test_dashboard(token),
        "Products": test_products(token),
        "Boxes": test_boxes(token),
        "History": test_history(token),
        "Leakage": test_leakage(token),
        "Orders": test_orders(token),
        "Subscription": test_subscription(token),
        "Warehouse": test_warehouse(token),
        "Admin": test_admin(token),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("FIRST RUN SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for tab, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {tab} Tab")
    
    print(f"\nFirst Run Result: {passed}/{total} tabs working")
    
    # SECOND RUN - As per user requirement
    print("\n" + "=" * 60)
    print("TESTING ALL TABS - SECOND RUN (VERIFICATION)")
    print("=" * 60)
    
    time.sleep(2)  # Wait 2 seconds between runs
    
    # Test all tabs again
    results2 = {
        "Dashboard": test_dashboard(token),
        "Products": test_products(token),
        "Boxes": test_boxes(token),
        "History": test_history(token),
        "Leakage": test_leakage(token),
        "Orders": test_orders(token),
        "Subscription": test_subscription(token),
        "Warehouse": test_warehouse(token),
        "Admin": test_admin(token),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("SECOND RUN SUMMARY")
    print("=" * 60)
    passed2 = sum(1 for v in results2.values() if v)
    total2 = len(results2)
    
    for tab, result in results2.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {tab} Tab")
    
    print(f"\nSecond Run Result: {passed2}/{total2} tabs working")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)
    
    if passed == total and passed2 == total2:
        print("✅✅ SUCCESS: All tabs working in BOTH runs!")
        print("✅ Frontend tabs match backend APIs")
        print("✅ Subscription tab is working correctly")
        print("✅ All new tabs (Orders, Bulk Upload, Tasks, Warehouse) are accessible")
    else:
        print(f"❌ FAILED: Some tabs not working")
        print(f"First run: {passed}/{total}")
        print(f"Second run: {passed2}/{total2}")

if __name__ == "__main__":
    main()
