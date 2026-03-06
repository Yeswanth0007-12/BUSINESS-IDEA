"""
Test script for enterprise features
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.json()}")
    return response.status_code == 200

def test_register_and_login():
    """Register a new user and login"""
    # Register
    register_data = {
        "email": "enterprise@test.com",
        "password": "testpass123",
        "company_name": "Enterprise Test Co"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code in [200, 201]:
        print(f"✓ User registered successfully")
        token = response.json()["access_token"]
        return token
    elif response.status_code == 400 and "already registered" in response.json()["detail"]:
        # User already exists, try to login
        print("  User already exists, logging in...")
        login_data = {
            "email": "enterprise@test.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print(f"✓ User logged in successfully")
            token = response.json()["access_token"]
            return token
    
    print(f"✗ Registration/Login failed: {response.status_code} - {response.text}")
    return None

def test_subscription_endpoints(token):
    """Test subscription endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # List subscription plans
    response = requests.get(f"{BASE_URL}/subscriptions/plans", headers=headers)
    if response.status_code == 200:
        plans = response.json()
        print(f"✓ Subscription plans retrieved: {len(plans)} plans available")
        for plan in plans:
            print(f"  - {plan['name']}: ${plan['price_monthly']}/month")
    else:
        print(f"✗ Failed to get subscription plans: {response.status_code}")
        return False
    
    # Get current subscription
    response = requests.get(f"{BASE_URL}/subscriptions/current", headers=headers)
    if response.status_code == 200:
        subscription = response.json()
        print(f"✓ Current subscription: {subscription.get('plan', {}).get('name', 'N/A')}")
    else:
        print(f"✗ Failed to get current subscription: {response.status_code}")
    
    # Get usage summary
    response = requests.get(f"{BASE_URL}/subscriptions/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Usage summary:")
        print(f"  - Products: {usage['total_products']}")
        print(f"  - Boxes: {usage['total_boxes']}")
        print(f"  - Optimizations this month: {usage['optimizations_this_month']}")
        print(f"  - Limit reached: {usage['limit_reached']}")
    else:
        print(f"✗ Failed to get usage summary: {response.status_code}")
    
    return True

def test_admin_endpoints(token):
    """Test admin endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # List company users
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        print(f"✓ Company users retrieved: {len(users)} users")
        for user in users:
            print(f"  - {user['email']} (Role: {user.get('role', 'N/A')})")
    else:
        print(f"✗ Failed to get company users: {response.status_code}")
        return False
    
    return True

def test_export_endpoints(token):
    """Test export endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Export products
    response = requests.get(f"{BASE_URL}/export/products", headers=headers)
    if response.status_code == 200:
        print(f"✓ Products export successful ({len(response.content)} bytes)")
    else:
        print(f"✗ Failed to export products: {response.status_code}")
    
    # Export boxes
    response = requests.get(f"{BASE_URL}/export/boxes", headers=headers)
    if response.status_code == 200:
        print(f"✓ Boxes export successful ({len(response.content)} bytes)")
    else:
        print(f"✗ Failed to export boxes: {response.status_code}")
    
    return True

def main():
    print("=" * 60)
    print("ENTERPRISE FEATURES TEST")
    print("=" * 60)
    print()
    
    # Test health
    print("1. Testing Health Endpoint...")
    if not test_health():
        print("Health check failed!")
        return
    print()
    
    # Register and login
    print("2. Testing Authentication...")
    token = test_register_and_login()
    if not token:
        print("Authentication failed!")
        return
    print()
    
    # Test subscription endpoints
    print("3. Testing Subscription Endpoints...")
    test_subscription_endpoints(token)
    print()
    
    # Test admin endpoints
    print("4. Testing Admin Endpoints...")
    test_admin_endpoints(token)
    print()
    
    # Test export endpoints
    print("5. Testing Export Endpoints...")
    test_export_endpoints(token)
    print()
    
    print("=" * 60)
    print("ENTERPRISE FEATURES TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
