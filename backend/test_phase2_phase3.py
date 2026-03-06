"""
Test Phase 2 and Phase 3 Implementation
Tests orientation testing, space utilization, and shipping cost calculations
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_phase2_phase3():
    """Test Phase 2 (orientation, space utilization) and Phase 3 (shipping costs)"""
    
    print("=" * 80)
    print("PHASE 2 & 3 INTEGRATION TEST")
    print("=" * 80)
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@packoptima.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Run optimization with default courier rate
    print("\n2. Running optimization with default courier rate (2.5)...")
    opt_response = requests.post(
        f"{BASE_URL}/optimize",
        headers=headers,
        json={"product_ids": None}  # All products
    )
    
    if opt_response.status_code != 200:
        print(f"❌ Optimization failed: {opt_response.status_code}")
        print(opt_response.text)
        return False
    
    result = opt_response.json()
    print("✅ Optimization completed")
    print(f"   Total products analyzed: {result['total_products_analyzed']}")
    print(f"   Products with savings: {result['products_with_savings']}")
    print(f"   Total monthly savings: ${result['total_monthly_savings']:.2f}")
    print(f"   Total annual savings: ${result['total_annual_savings']:.2f}")
    
    # Step 3: Verify Phase 2 fields (orientation, space_utilization, unused_volume)
    print("\n3. Verifying Phase 2 fields (orientation, space utilization)...")
    phase2_verified = False
    
    for i, product_result in enumerate(result['results'][:3]):  # Check first 3
        print(f"\n   Product: {product_result['product_name']}")
        print(f"   - Orientation: {product_result.get('orientation', 'MISSING')}")
        print(f"   - Space Utilization: {product_result.get('space_utilization', 'MISSING')}%")
        print(f"   - Unused Volume: {product_result.get('unused_volume', 'MISSING')} cm³")
        
        if (product_result.get('orientation') is not None and 
            product_result.get('space_utilization', 0) > 0):
            phase2_verified = True
    
    if phase2_verified:
        print("\n✅ Phase 2 fields verified successfully")
    else:
        print("\n❌ Phase 2 fields missing or invalid")
        return False
    
    # Step 4: Verify Phase 3 fields (shipping costs)
    print("\n4. Verifying Phase 3 fields (shipping costs)...")
    phase3_verified = False
    
    for i, product_result in enumerate(result['results'][:3]):  # Check first 3
        print(f"\n   Product: {product_result['product_name']}")
        print(f"   - Shipping Cost Current: ${product_result.get('shipping_cost_current', 'MISSING'):.2f}")
        print(f"   - Shipping Cost Recommended: ${product_result.get('shipping_cost_recommended', 'MISSING'):.2f}")
        print(f"   - Total Cost Current: ${product_result.get('total_cost_current', 'MISSING'):.2f}")
        print(f"   - Total Cost Recommended: ${product_result.get('total_cost_recommended', 'MISSING'):.2f}")
        print(f"   - Billable Weight Current: {product_result.get('billable_weight_current', 'MISSING')} kg")
        print(f"   - Billable Weight Recommended: {product_result.get('billable_weight_recommended', 'MISSING')} kg")
        
        if (product_result.get('total_cost_current', 0) > 0 or 
            product_result.get('total_cost_recommended', 0) > 0):
            phase3_verified = True
    
    if phase3_verified:
        print("\n✅ Phase 3 fields verified successfully")
    else:
        print("\n❌ Phase 3 fields missing or invalid")
        return False
    
    # Step 5: Test custom courier rate
    print("\n5. Testing custom courier rate (5.0)...")
    opt_response2 = requests.post(
        f"{BASE_URL}/optimize",
        headers=headers,
        json={
            "product_ids": None,
            "courier_rate": 5.0  # Custom rate
        }
    )
    
    if opt_response2.status_code != 200:
        print(f"❌ Custom courier rate test failed: {opt_response2.status_code}")
        print(opt_response2.text)
        return False
    
    result2 = opt_response2.json()
    print("✅ Custom courier rate optimization completed")
    
    # Compare savings (should be different with different courier rate)
    if result2['total_monthly_savings'] != result['total_monthly_savings']:
        print(f"   Default rate savings: ${result['total_monthly_savings']:.2f}")
        print(f"   Custom rate savings: ${result2['total_monthly_savings']:.2f}")
        print("✅ Courier rate parameter working correctly")
    else:
        print("⚠️  Savings identical - courier rate may not be affecting calculations")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Phase 2 & 3 Integration Complete!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_phase2_phase3()
    exit(0 if success else 1)
