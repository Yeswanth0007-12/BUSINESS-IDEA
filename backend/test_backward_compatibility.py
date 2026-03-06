"""
Test backward compatibility for migration 004
Tests:
1. Existing API endpoints work without new fields
2. Creating products/boxes with new fields works
3. Creating products/boxes without new fields uses defaults
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    # Try to login with existing user (JSON format)
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@packoptima.com",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # Try another common admin account
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register
    import random
    email = f"test_migration_{random.randint(1000, 9999)}@packoptima.com"
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": "testpass123",
            "company_name": "Test Migration Co"
        }
    )
    
    if response.status_code == 201:
        return response.json()["access_token"]
    
    print(f"Registration failed: {response.status_code} - {response.text}")
    raise Exception("Could not authenticate")

def test_backward_compatibility():
    """Run backward compatibility tests"""
    print("=" * 60)
    print("TESTING BACKWARD COMPATIBILITY")
    print("=" * 60)
    
    try:
        # Get auth token
        print("\n1. Authenticating...")
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✓ Authentication successful")
        
        # Test 1: Create product WITHOUT new fields (should use defaults)
        print("\n2. Creating product WITHOUT new fields...")
        import random
        sku_suffix = random.randint(1000, 9999)
        product_data = {
            "name": "Test Product Legacy",
            "sku": f"TEST-LEGACY-{sku_suffix}",
            "category": "electronics",
            "length_cm": 10.0,
            "width_cm": 8.0,
            "height_cm": 5.0,
            "weight_kg": 0.5,
            "monthly_order_volume": 100
        }
        
        response = requests.post(
            f"{BASE_URL}/products",
            json=product_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            product = response.json()
            print(f"   ✓ Product created: {product['name']}")
            print(f"     - fragile: {product.get('fragile', 'NOT IN RESPONSE')}")
            print(f"     - stackable: {product.get('stackable', 'NOT IN RESPONSE')}")
            
            # Verify defaults were applied
            if product.get('fragile') == False and product.get('stackable') == True:
                print("   ✓ Default values applied correctly")
            else:
                print("   ✗ Default values not applied correctly!")
                return False
            
            legacy_product_id = product['id']
        else:
            print(f"   ✗ Failed to create product: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
        
        # Test 2: Create product WITH new fields
        print("\n3. Creating product WITH new fields...")
        sku_suffix = random.randint(1000, 9999)
        product_data_new = {
            "name": "Test Product New",
            "sku": f"TEST-NEW-{sku_suffix}",
            "category": "electronics",
            "length_cm": 10.0,
            "width_cm": 8.0,
            "height_cm": 5.0,
            "weight_kg": 0.5,
            "monthly_order_volume": 100,
            "fragile": True,
            "stackable": False
        }
        
        response = requests.post(
            f"{BASE_URL}/products",
            json=product_data_new,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            product = response.json()
            print(f"   ✓ Product created: {product['name']}")
            print(f"     - fragile: {product.get('fragile')}")
            print(f"     - stackable: {product.get('stackable')}")
            
            # Verify new values were set
            if product.get('fragile') == True and product.get('stackable') == False:
                print("   ✓ New field values set correctly")
            else:
                print("   ✗ New field values not set correctly!")
                return False
            
            new_product_id = product['id']
        else:
            print(f"   ✗ Failed to create product: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
        
        # Test 3: Create box WITHOUT new fields (should use defaults)
        print("\n4. Creating box WITHOUT new fields...")
        box_data = {
            "name": f"Test Box Legacy {random.randint(1000, 9999)}",
            "length_cm": 20.0,
            "width_cm": 15.0,
            "height_cm": 10.0,
            "cost_per_unit": 0.50
        }
        
        response = requests.post(
            f"{BASE_URL}/boxes",
            json=box_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            box = response.json()
            print(f"   ✓ Box created: {box['name']}")
            print(f"     - max_weight_kg: {box.get('max_weight_kg', 'NOT IN RESPONSE')}")
            print(f"     - material_type: {box.get('material_type', 'NOT IN RESPONSE')}")
            
            # Verify defaults were applied
            if box.get('max_weight_kg') == 30.0 and box.get('material_type') == 'cardboard':
                print("   ✓ Default values applied correctly")
            else:
                print("   ✗ Default values not applied correctly!")
                return False
            
            legacy_box_id = box['id']
        else:
            print(f"   ✗ Failed to create box: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
        
        # Test 4: Create box WITH new fields
        print("\n5. Creating box WITH new fields...")
        box_data_new = {
            "name": f"Test Box New {random.randint(1000, 9999)}",
            "length_cm": 20.0,
            "width_cm": 15.0,
            "height_cm": 10.0,
            "cost_per_unit": 0.75,
            "max_weight_kg": 50.0,
            "material_type": "plastic"
        }
        
        response = requests.post(
            f"{BASE_URL}/boxes",
            json=box_data_new,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            box = response.json()
            print(f"   ✓ Box created: {box['name']}")
            print(f"     - max_weight_kg: {box.get('max_weight_kg')}")
            print(f"     - material_type: {box.get('material_type')}")
            
            # Verify new values were set
            if box.get('max_weight_kg') == 50.0 and box.get('material_type') == 'plastic':
                print("   ✓ New field values set correctly")
            else:
                print("   ✗ New field values not set correctly!")
                return False
            
            new_box_id = box['id']
        else:
            print(f"   ✗ Failed to create box: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
        
        # Test 5: Retrieve products and verify fields are in response
        print("\n6. Retrieving products to verify response format...")
        response = requests.get(
            f"{BASE_URL}/products/{legacy_product_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            product = response.json()
            if 'fragile' in product and 'stackable' in product:
                print("   ✓ Product response includes new fields")
            else:
                print("   ✗ Product response missing new fields!")
                return False
        else:
            print(f"   ✗ Failed to retrieve product: {response.status_code}")
            return False
        
        # Test 6: Retrieve boxes and verify fields are in response
        print("\n7. Retrieving boxes to verify response format...")
        response = requests.get(
            f"{BASE_URL}/boxes/{legacy_box_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            box = response.json()
            if 'max_weight_kg' in box and 'material_type' in box:
                print("   ✓ Box response includes new fields")
            else:
                print("   ✗ Box response missing new fields!")
                return False
        else:
            print(f"   ✗ Failed to retrieve box: {response.status_code}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ ALL BACKWARD COMPATIBILITY TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backward_compatibility()
    sys.exit(0 if success else 1)
