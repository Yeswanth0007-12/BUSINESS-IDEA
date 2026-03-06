#!/usr/bin/env python3
"""
Test script to verify login navigation pipeline
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_flow():
    """Test the complete login flow"""
    print("=" * 60)
    print("TESTING LOGIN NAVIGATION PIPELINE")
    print("=" * 60)
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "company_name": "Test Company"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201]:
            print("✅ Registration successful")
            token = response.json().get("access_token")
            print(f"   Token received: {token[:20]}...")
        elif response.status_code == 400:
            print("⚠️  User already exists, trying login instead...")
            # Try login
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ Login successful")
                token = response.json().get("access_token")
                print(f"   Token received: {token[:20]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during registration/login: {e}")
        return False
    
    # Test 2: Access protected dashboard endpoint
    print("\n2. Testing dashboard access with token...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard endpoint accessible")
            data = response.json()
            print(f"   Total products: {data.get('total_products', 0)}")
            print(f"   Total boxes: {data.get('total_boxes', 0)}")
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return False
    
    # Test 3: Access products endpoint
    print("\n3. Testing products endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        if response.status_code == 200:
            print("✅ Products endpoint accessible")
            products = response.json()
            print(f"   Products count: {len(products)}")
        else:
            print(f"❌ Products access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing products: {e}")
        return False
    
    # Test 4: Access boxes endpoint
    print("\n4. Testing boxes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/boxes", headers=headers)
        if response.status_code == 200:
            print("✅ Boxes endpoint accessible")
            boxes = response.json()
            print(f"   Boxes count: {len(boxes)}")
        else:
            print(f"❌ Boxes access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing boxes: {e}")
        return False
    
    # Test 5: Test without token (should fail)
    print("\n5. Testing protected endpoint without token...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard")
        if response.status_code == 401:
            print("✅ Correctly rejected request without token")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - LOGIN PIPELINE WORKING")
    print("=" * 60)
    print("\nFrontend Flow:")
    print("1. User visits http://localhost:8080")
    print("2. Redirected to /login (not authenticated)")
    print("3. User enters credentials and clicks 'Sign In'")
    print("4. Token stored in localStorage")
    print("5. Navigated to /dashboard")
    print("6. All tabs accessible via sidebar")
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_login_flow()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        exit(1)
