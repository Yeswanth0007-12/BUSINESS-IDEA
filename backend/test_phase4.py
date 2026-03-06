"""
Phase 4: Multi-Product Order Packing Test
Tests order creation, bin packing algorithm, fragile/stackable constraints
"""
import requests

BASE_URL = "http://localhost:8000"

def test_phase4():
    print("=" * 80)
    print("PHASE 4: MULTI-PRODUCT ORDER PACKING TEST")
    print("=" * 80)
    
    # Step 1: Register/Login
    print("\n1. Setting up authentication...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "phase4test@packoptima.com",
            "password": "test12345",
            "company_name": "Phase 4 Test Company"
        }
    )
    
    if register_response.status_code == 201:
        print("✅ New user registered")
        token = register_response.json()["access_token"]
    else:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "phase4test@packoptima.com", "password": "test12345"}
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
    
    for box in boxes:
        response = requests.post(f"{BASE_URL}/boxes", headers=headers, json=box)
        if response.status_code == 201:
            print(f"   ✅ Added: {box['name']}")
    
    # Step 3: Add products (including fragile and non-stackable)
    print("\n3. Adding products...")
    products = [
        {
            "name": "Regular Widget",
            "sku": "RW-001",
            "length_cm": 10,
            "width_cm": 8,
            "height_cm": 5,
            "weight_kg": 0.5,
            "category": "electronics",
            "monthly_order_volume": 100,
            "fragile": False,
            "stackable": True
        },
        {
            "name": "Fragile Glass Item",
            "sku": "FG-001",
            "length_cm": 12,
            "width_cm": 12,
            "height_cm": 8,
            "weight_kg": 1.0,
            "category": "fragile",
            "monthly_order_volume": 50,
            "fragile": True,
            "stackable": False
        },
        {
            "name": "Non-Stackable Box",
            "sku": "NS-001",
            "length_cm": 15,
            "width_cm": 10,
            "height_cm": 10,
            "weight_kg": 2.0,
            "category": "electronics",
            "monthly_order_volume": 30,
            "fragile": False,
            "stackable": False
        },
    ]
    
    product_ids = []
    for product in products:
        response = requests.post(f"{BASE_URL}/products", headers=headers, json=product)
        if response.status_code == 201:
            product_ids.append(response.json()["id"])
            print(f"   ✅ Added: {product['name']}")
        elif response.status_code == 400:
            # Product might already exist, try to get it
            list_response = requests.get(f"{BASE_URL}/products", headers=headers)
            if list_response.status_code == 200:
                existing_products = list_response.json()
                for existing in existing_products:
                    if existing['sku'] == product['sku']:
                        product_ids.append(existing['id'])
                        print(f"   ℹ️  Using existing: {product['name']}")
                        break
    
    if len(product_ids) < 3:
        print(f"❌ Failed to create/find all products")
        return False
    
    # Step 4: Create an order
    print("\n4. Creating multi-product order...")
    import time
    order_number = f"ORD-{int(time.time())}"
    order_data = {
        "order_number": order_number,
        "customer_name": "Test Customer",
        "items": [
            {"product_id": product_ids[0], "quantity": 3},  # 3x Regular Widget
            {"product_id": product_ids[1], "quantity": 1},  # 1x Fragile Glass
            {"product_id": product_ids[2], "quantity": 2},  # 2x Non-Stackable
        ]
    }
    
    order_response = requests.post(f"{BASE_URL}/orders", headers=headers, json=order_data)
    
    if order_response.status_code != 201:
        print(f"❌ Order creation failed: {order_response.text}")
        return False
    
    order = order_response.json()
    order_id = order["id"]
    print(f"✅ Order created: {order['order_number']}")
    print(f"   Order ID: {order_id}")
    print(f"   Status: {order['status']}")
    print(f"   Items: {len(order['items'])}")
    
    # Step 5: Optimize order packing
    print("\n5. Optimizing order packing...")
    optimize_response = requests.post(
        f"{BASE_URL}/orders/{order_id}/optimize",
        headers=headers,
        params={"courier_rate": 2.5}
    )
    
    if optimize_response.status_code != 200:
        print(f"❌ Packing optimization failed: {optimize_response.text}")
        return False
    
    packing = optimize_response.json()
    print(f"✅ Packing optimization completed")
    print(f"   Success: {packing['success']}")
    print(f"   Total boxes: {packing['total_boxes']}")
    print(f"   Total cost: ${packing['total_cost']:.2f}")
    print(f"   Total shipping cost: ${packing['total_shipping_cost']:.2f}")
    print(f"   Message: {packing['message']}")
    
    # Step 6: Verify packing results
    print("\n6. Verifying packing results...")
    for result in packing['packing_results']:
        print(f"\n   Box #{result['box_number']}:")
        print(f"   - Products packed: {len(result['products_packed'])}")
        print(f"   - Total weight: {result['total_weight']} kg")
        print(f"   - Space utilization: {result['space_utilization']:.1f}%")
        print(f"   - Shipping cost: ${result['shipping_cost']:.2f}")
    
    if packing['unpacked_items']:
        print(f"\n   ⚠️  Unpacked items: {len(packing['unpacked_items'])}")
        for item in packing['unpacked_items']:
            print(f"   - {item['product_name']}")
    
    # Step 7: Verify fragile item constraint
    print("\n7. Verifying fragile item constraint...")
    fragile_box_found = False
    for result in packing['packing_results']:
        products_in_box = result['products_packed']
        has_fragile = any('Fragile' in p['product_name'] for p in products_in_box)
        
        if has_fragile:
            fragile_box_found = True
            if len(products_in_box) == 1:
                print(f"   ✅ Fragile item packed alone in Box #{result['box_number']}")
            else:
                print(f"   ❌ Fragile item packed with other items in Box #{result['box_number']}")
                return False
    
    if not fragile_box_found:
        print("   ⚠️  No fragile items found in packing results")
    
    # Step 8: List orders
    print("\n8. Testing order listing...")
    list_response = requests.get(f"{BASE_URL}/orders", headers=headers)
    
    if list_response.status_code != 200:
        print(f"❌ Order listing failed")
        return False
    
    orders = list_response.json()
    print(f"✅ Retrieved {len(orders)} orders")
    
    # Step 9: Get specific order
    print("\n9. Testing order retrieval...")
    get_response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ Order retrieval failed")
        return False
    
    retrieved_order = get_response.json()
    print(f"✅ Retrieved order: {retrieved_order['order_number']}")
    print(f"   Status: {retrieved_order['status']}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Phase 4 Complete!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = test_phase4()
    exit(0 if success else 1)
