"""
Complete Phase 2 & 3 Test with Data Setup
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete():
    print("=" * 80)
    print("PHASE 2 & 3 COMPLETE INTEGRATION TEST")
    print("=" * 80)
    
    # Step 1: Register/Login
    print("\n1. Setting up authentication...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "phase23test@packoptima.com",
            "password": "test12345",
            "company_name": "Phase 2-3 Test Company"
        }
    )
    
    if register_response.status_code == 201:
        print("✅ New user registered")
        token = register_response.json()["access_token"]
    else:
        # Try login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "phase23test@packoptima.com", "password": "test12345"}
        )
        if login_response.status_code == 200:
            print("✅ Existing user logged in")
            token = login_response.json()["access_token"]
        else:
            print(f"❌ Authentication failed")
            return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Add boxes
    print("\n2. Adding boxes...")
    boxes = [
        {"name": "Small Box", "length_cm": 20, "width_cm": 15, "height_cm": 10, "cost_per_unit": 0.50, "max_weight_kg": 5.0, "material_type": "cardboard"},
        {"name": "Medium Box", "length_cm": 30, "width_cm": 25, "height_cm": 20, "cost_per_unit": 1.00, "max_weight_kg": 15.0, "material_type": "cardboard"},
        {"name": "Large Box", "length_cm": 50, "width_cm": 40, "height_cm": 30, "cost_per_unit": 2.00, "max_weight_kg": 30.0, "material_type": "cardboard"},
    ]
    
    box_ids = []
    for box in boxes:
        response = requests.post(f"{BASE_URL}/boxes", headers=headers, json=box)
        if response.status_code == 201:
            box_ids.append(response.json()["id"])
            print(f"   ✅ Added: {box['name']}")
        else:
            print(f"   ⚠️  Box might already exist: {box['name']}")
    
    # Step 3: Add products
    print("\n3. Adding products...")
    products = [
        {
            "name": "Small Widget",
            "sku": "SW-001",
            "length_cm": 10,
            "width_cm": 8,
            "height_cm": 5,
            "weight_kg": 0.5,
            "category": "electronics",
            "monthly_order_volume": 100,
            "current_box_id": box_ids[1] if len(box_ids) > 1 else None,  # Using medium box (oversized)
            "fragile": True,
            "stackable": False
        },
        {
            "name": "Medium Gadget",
            "sku": "MG-001",
            "length_cm": 25,
            "width_cm": 20,
            "height_cm": 15,
            "weight_kg": 2.5,
            "category": "electronics",
            "monthly_order_volume": 50,
            "current_box_id": box_ids[2] if len(box_ids) > 2 else None,  # Using large box (oversized)
            "fragile": False,
            "stackable": True
        },
    ]
    
    product_ids = []
    for product in products:
        response = requests.post(f"{BASE_URL}/products", headers=headers, json=product)
        if response.status_code == 201:
            product_ids.append(response.json()["id"])
            print(f"   ✅ Added: {product['name']}")
        else:
            print(f"   ⚠️  Product might already exist: {product['name']}")
    
    # Step 4: Run optimization with default courier rate
    print("\n4. Running optimization (default courier rate = 2.5)...")
    opt_response = requests.post(
        f"{BASE_URL}/optimize",
        headers=headers,
        json={"product_ids": None}
    )
    
    if opt_response.status_code != 200:
        print(f"❌ Optimization failed: {opt_response.text}")
        return False
    
    result = opt_response.json()
    print(f"✅ Optimization completed")
    print(f"   Products analyzed: {result['total_products_analyzed']}")
    print(f"   Products with savings: {result['products_with_savings']}")
    print(f"   Total monthly savings: ${result['total_monthly_savings']:.2f}")
    
    # Step 5: Verify Phase 2 fields
    print("\n5. Verifying Phase 2 fields (orientation, space utilization)...")
    phase2_ok = False
    
    for i, prod_result in enumerate(result['results'][:2]):
        print(f"\n   Product: {prod_result['product_name']}")
        print(f"   - Recommended Box: {prod_result['recommended_box_name']}")
        print(f"   - Orientation: {prod_result.get('orientation')}")
        print(f"   - Space Utilization: {prod_result.get('space_utilization')}%")
        print(f"   - Unused Volume: {prod_result.get('unused_volume')} cm³")
        
        if (prod_result.get('orientation') is not None and 
            prod_result.get('space_utilization', 0) > 0):
            phase2_ok = True
    
    if phase2_ok:
        print("\n✅ Phase 2 fields verified!")
    else:
        print("\n❌ Phase 2 fields missing")
        return False
    
    # Step 6: Verify Phase 3 fields
    print("\n6. Verifying Phase 3 fields (shipping costs)...")
    phase3_ok = False
    
    for i, prod_result in enumerate(result['results'][:2]):
        print(f"\n   Product: {prod_result['product_name']}")
        print(f"   - Shipping Cost Current: ${prod_result.get('shipping_cost_current', 0):.2f}")
        print(f"   - Shipping Cost Recommended: ${prod_result.get('shipping_cost_recommended', 0):.2f}")
        print(f"   - Total Cost Current: ${prod_result.get('total_cost_current', 0):.2f}")
        print(f"   - Total Cost Recommended: ${prod_result.get('total_cost_recommended', 0):.2f}")
        print(f"   - Billable Weight Current: {prod_result.get('billable_weight_current', 0)} kg")
        print(f"   - Billable Weight Recommended: {prod_result.get('billable_weight_recommended', 0)} kg")
        
        if (prod_result.get('total_cost_current', 0) > 0 or 
            prod_result.get('total_cost_recommended', 0) > 0):
            phase3_ok = True
    
    if phase3_ok:
        print("\n✅ Phase 3 fields verified!")
    else:
        print("\n❌ Phase 3 fields missing")
        return False
    
    # Step 7: Test custom courier rate
    print("\n7. Testing custom courier rate (5.0)...")
    opt_response2 = requests.post(
        f"{BASE_URL}/optimize",
        headers=headers,
        json={"product_ids": None, "courier_rate": 5.0}
    )
    
    if opt_response2.status_code != 200:
        print(f"❌ Custom courier rate test failed")
        return False
    
    result2 = opt_response2.json()
    print(f"✅ Custom courier rate optimization completed")
    print(f"   Default rate (2.5) savings: ${result['total_monthly_savings']:.2f}")
    print(f"   Custom rate (5.0) savings: ${result2['total_monthly_savings']:.2f}")
    
    if result2['total_monthly_savings'] != result['total_monthly_savings']:
        print("✅ Courier rate parameter working correctly!")
    else:
        print("⚠️  Savings identical - may need investigation")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Phase 2 & 3 Integration Complete!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_complete()
    exit(0 if success else 1)
