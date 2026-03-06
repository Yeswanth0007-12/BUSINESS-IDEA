#!/usr/bin/env python3
"""
Test Login Flow - Verify authentication and navigation works correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

def test_login_flow():
    """Test the complete login flow"""
    print("\n" + "="*60)
    print("         Testing Login Flow")
    print("="*60 + "\n")
    
    # Test 1: Register a new user
    print("1. Testing User Registration...")
    register_data = {
        "email": f"testuser_{int(time.time())}@example.com",
        "password": "testpass123",
        "company_name": "Test Company"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("   ✓ Registration successful")
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   ✓ Received access token: {access_token[:20]}...")
        else:
            print(f"   ✗ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Registration error: {e}")
        return False
    
    # Test 2: Login with the same credentials
    print("\n2. Testing User Login...")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("   ✓ Login successful")
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"   ✓ Received access token: {access_token[:20]}...")
        else:
            print(f"   ✗ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return False
    
    # Test 3: Access protected endpoint with token
    print("\n3. Testing Protected Endpoint Access...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            print("   ✓ Successfully accessed protected endpoint")
            products = response.json()
            print(f"   ✓ Retrieved {len(products)} products")
        else:
            print(f"   ✗ Failed to access protected endpoint: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Protected endpoint error: {e}")
        return False
    
    # Test 4: Check frontend is accessible
    print("\n4. Testing Frontend Accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("   ✓ Frontend is accessible")
        else:
            print(f"   ✗ Frontend returned status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Frontend error: {e}")
    
    print("\n" + "="*60)
    print("✓ All login flow tests passed!")
    print("="*60 + "\n")
    
    print("Next Steps:")
    print("1. Open http://localhost:8080 in your browser")
    print("2. Click 'Register here' to create a new account")
    print("3. Fill in the form with:")
    print("   - Email: your@email.com")
    print("   - Company Name: Your Company")
    print("   - Password: at least 8 characters")
    print("4. After registration, you should be redirected to the dashboard")
    print("5. You can then navigate to other tabs:")
    print("   - Products: Add and manage products")
    print("   - Boxes: Add and manage box sizes")
    print("   - Optimize: Run optimization algorithm")
    print("   - History: View past optimization runs")
    print("   - Leakage: View space utilization analysis")
    
    return True

if __name__ == "__main__":
    test_login_flow()
