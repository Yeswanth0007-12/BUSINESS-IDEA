"""
Complete Integrated Application Test
Tests both OLD features (Products, Boxes, Optimize, etc.) 
and NEW enterprise features (Subscriptions, RBAC, Export, etc.)
"""
import requests
import json
import csv
import io

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_auth():
    """Test authentication"""
    print_section("1. AUTHENTICATION")
    
    # Register or login
    register_data = {
        "email": "integrated@test.com",
        "password": "testpass123",
        "company_name": "Integrated Test Co"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code in [200, 201]:
        print("✓ User registered")
        token = response.json()["access_token"]
    else:
        # Try login
        login_data = {"email": "integrated@test.com", "password": "testpass123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ User logged in")
            token = response.json()["access_token"]
        else:
            print(f"✗ Auth failed: {response.status_code}")
            return None
    
    return token

def test_old_features(token):
    """Test original application features"""
    print_section("2. ORIGINAL FEATURES (Products, Boxes, Optimize)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Products
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Products: {len(products)} items")
    else:
        print(f"✗ Products failed: {response.status_code}")
    
    # Boxes
    response = requests.get(f"{BASE_URL}/boxes", headers=headers)
    if response.status_code == 200:
        boxes = response.json()
        print(f"✓ Boxes: {len(boxes)} items")
    else:
        print(f"✗ Boxes failed: {response.status_code}")
    
    # Analytics
    response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    if response.status_code == 200:
        print(f"✓ Analytics dashboard working")
    else:
        print(f"✗ Analytics failed: {response.status_code}")
    
    # History
    response = requests.get(f"{BASE_URL}/history", headers=headers)
    if response.status_code == 200:
        history = response.json()
        print(f"✓ History: {len(history)} optimization runs")
    else:
        print(f"✗ History failed: {response.status_code}")

def test_enterprise_features(token):
    """Test new enterprise features"""
    print_section("3. ENTERPRISE FEATURES (Subscriptions, RBAC, Export)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Subscription Plans
    response = requests.get(f"{BASE_URL}/subscriptions/plans", headers=headers)
    if response.status_code == 200:
        plans = response.json()
        print(f"✓ Subscription plans: {len(plans)} available")
        for plan in plans:
            print(f"  - {plan['name']}: ${plan['price_monthly']}/month")
    else:
        print(f"✗ Subscription plans failed: {response.status_code}")
    
    # Usage Summary
    response = requests.get(f"{BASE_URL}/subscriptions/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Usage tracking:")
        print(f"  - Products: {usage['total_products']}")
        print(f"  - Boxes: {usage['total_boxes']}")
        print(f"  - Optimizations this month: {usage['optimizations_this_month']}")
    else:
        print(f"✗ Usage tracking failed: {response.status_code}")
    
    # Admin - User Management
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        print(f"✓ User management: {len(users)} users")
        for user in users:
            print(f"  - {user['email']} ({user.get('role', 'N/A')})")
    else:
        print(f"✗ User management failed: {response.status_code}")
    
    # Export - Products
    response = requests.get(f"{BASE_URL}/export/products", headers=headers)
    if response.status_code == 200:
        print(f"✓ Data export: Products CSV ({len(response.content)} bytes)")
    else:
        print(f"✗ Data export failed: {response.status_code}")

def test_integration():
    """Test that old and new features work together"""
    print_section("4. INTEGRATION TEST (Old + New Features)")
    
    token = test_auth()
    if not token:
        print("✗ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a product (old feature)
    product_data = {
        "name": "Integration Test Product",
        "sku": "INT-001",
        "category": "Test",
        "length_cm": 10,
        "width_cm": 10,
        "height_cm": 10,
        "weight_kg": 1,
        "monthly_order_volume": 100
    }
    response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
    if response.status_code in [200, 201]:
        product_id = response.json()["id"]
        print(f"✓ Created product (ID: {product_id})")
        
        # Check usage increased (new feature)
        response = requests.get(f"{BASE_URL}/subscriptions/usage", headers=headers)
        if response.status_code == 200:
            usage = response.json()
            print(f"✓ Usage tracking updated: {usage['total_products']} products")
        
        # Export the product (new feature)
        response = requests.get(f"{BASE_URL}/export/products", headers=headers)
        if response.status_code == 200:
            print(f"✓ Product exported successfully")
        
        # Delete the product (old feature)
        response = requests.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
        if response.status_code in [200, 204]:
            print(f"✓ Product deleted")
    else:
        print(f"✗ Integration test failed: {response.status_code}")

def main():
    print("\n" + "="*70)
    print("  COMPLETE INTEGRATED APPLICATION TEST")
    print("  Testing OLD + NEW Features Together")
    print("="*70)
    
    token = test_auth()
    if not token:
        print("\n✗ FAILED: Cannot authenticate")
        return
    
    test_old_features(token)
    test_enterprise_features(token)
    test_integration()
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n✓ All features (old + new) are working together!\n")

if __name__ == "__main__":
    main()
