import requests

# Test if backend is accessible
try:
    response = requests.get("http://localhost:8000/docs")
    print(f"Backend accessible: {response.status_code}")
    
    # Try register first
    register_response = requests.post(
        "http://localhost:8000/auth/register",
        json={
            "email": "test@packoptima.com",
            "password": "test12345",  # At least 8 characters
            "company_name": "Test Company"
        }
    )
    print(f"Register response: {register_response.status_code}")
    
    if register_response.status_code == 201:
        print("✅ Registration successful")
        token = register_response.json()["access_token"]
    else:
        # Try login if registration fails (user might already exist)
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={"email": "test@packoptima.com", "password": "test12345"}
        )
        print(f"Login response: {login_response.status_code}")
        if login_response.status_code == 200:
            print("✅ Login successful")
            token = login_response.json()["access_token"]
        else:
            print(f"❌ Login failed: {login_response.text}")
            exit(1)
    
    # Try optimization
    opt_response = requests.post(
        "http://localhost:8000/optimize",
        headers={"Authorization": f"Bearer {token}"},
        json={"product_ids": None}
    )
    print(f"Optimization response: {opt_response.status_code}")
    if opt_response.status_code == 200:
        result = opt_response.json()
        print(f"✅ Optimization successful")
        print(f"   Products analyzed: {result['total_products_analyzed']}")
        
        # Check Phase 2 & 3 fields
        if result['results']:
            first_result = result['results'][0]
            print(f"\n   First product: {first_result['product_name']}")
            print(f"   - Orientation: {first_result.get('orientation')}")
            print(f"   - Space utilization: {first_result.get('space_utilization')}%")
            print(f"   - Shipping cost current: ${first_result.get('shipping_cost_current', 0):.2f}")
            print(f"   - Total cost current: ${first_result.get('total_cost_current', 0):.2f}")
            print("\n✅ Phase 2 & 3 fields present!")
        else:
            print("⚠️  No results returned (no products in database)")
    else:
        print(f"❌ Optimization failed: {opt_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
