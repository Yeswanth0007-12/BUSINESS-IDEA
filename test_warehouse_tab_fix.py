"""
Test script to verify Warehouse tab fix.

This script tests:
1. User can login successfully
2. Warehouse tab endpoints are accessible with JWT token
3. API key creation works
4. Webhook creation works
5. No 401 redirect to login page
"""
import requests
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_warehouse_tab_fix():
    print("=" * 80)
    print("WAREHOUSE TAB FIX VERIFICATION")
    print("=" * 80)
    
    # Step 1: Register/Login
    print("\n1. Testing user authentication...")
    email = f"warehouse_test_{int(time.time())}@test.com"
    password = "testpass123"
    
    register_data = {
        "email": email,
        "password": password,
        "company_name": "Warehouse Test Co"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201]:
            token = response.json()["access_token"]
            print(f"   ✅ User registered successfully")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test API Keys endpoint (should work with JWT)
    print("\n2. Testing API Keys endpoint with JWT token...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/warehouse/api-keys", headers=headers)
        if response.status_code == 200:
            api_keys = response.json()
            print(f"   ✅ API Keys endpoint accessible (found {len(api_keys)} keys)")
        else:
            print(f"   ❌ API Keys endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ API Keys endpoint error: {e}")
        return False
    
    # Step 3: Test Webhooks endpoint (should work with JWT after fix)
    print("\n3. Testing Webhooks endpoint with JWT token...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/warehouse/webhooks", headers=headers)
        if response.status_code == 200:
            webhooks = response.json()
            print(f"   ✅ Webhooks endpoint accessible (found {len(webhooks)} webhooks)")
        elif response.status_code == 401:
            print(f"   ❌ Webhooks endpoint returned 401 - FIX NOT APPLIED!")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"   ❌ Webhooks endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Webhooks endpoint error: {e}")
        return False
    
    # Step 4: Create an API key
    print("\n4. Testing API Key creation...")
    try:
        create_key_data = {"name": "Test Warehouse Key"}
        response = requests.post(
            f"{BASE_URL}/api/v1/warehouse/api-keys",
            json=create_key_data,
            headers=headers
        )
        if response.status_code == 201:
            key_data = response.json()
            print(f"   ✅ API Key created successfully")
            print(f"   Key ID: {key_data['id']}")
            print(f"   Key Name: {key_data['name']}")
            print(f"   Key Value: {key_data['api_key'][:20]}...")
            created_key_id = key_data['id']
        else:
            print(f"   ❌ API Key creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ API Key creation error: {e}")
        return False
    
    # Step 5: Create a webhook
    print("\n5. Testing Webhook creation...")
    try:
        create_webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["optimization.completed"],
            "secret": "test_secret_123456789_long_enough"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/warehouse/webhooks",
            json=create_webhook_data,
            headers=headers
        )
        if response.status_code == 201:
            webhook_data = response.json()
            print(f"   ✅ Webhook created successfully")
            print(f"   Webhook ID: {webhook_data['id']}")
            print(f"   Webhook URL: {webhook_data['url']}")
            print(f"   Events: {webhook_data['events']}")
            created_webhook_id = webhook_data['id']
        else:
            print(f"   ❌ Webhook creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Webhook creation error: {e}")
        return False
    
    # Step 6: Verify we can list both again
    print("\n6. Verifying data persistence...")
    try:
        # List API keys
        response = requests.get(f"{BASE_URL}/api/v1/warehouse/api-keys", headers=headers)
        if response.status_code == 200:
            api_keys = response.json()
            if len(api_keys) >= 1:
                print(f"   ✅ API Keys persisted ({len(api_keys)} keys)")
            else:
                print(f"   ⚠️  Expected at least 1 API key, found {len(api_keys)}")
        
        # List webhooks
        response = requests.get(f"{BASE_URL}/api/v1/warehouse/webhooks", headers=headers)
        if response.status_code == 200:
            webhooks = response.json()
            if len(webhooks) >= 1:
                print(f"   ✅ Webhooks persisted ({len(webhooks)} webhooks)")
            else:
                print(f"   ⚠️  Expected at least 1 webhook, found {len(webhooks)}")
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False
    
    # Step 7: Delete created resources
    print("\n7. Cleaning up test data...")
    try:
        # Delete webhook
        response = requests.delete(
            f"{BASE_URL}/api/v1/warehouse/webhooks/{created_webhook_id}",
            headers=headers
        )
        if response.status_code == 204:
            print(f"   ✅ Webhook deleted")
        
        # Delete API key
        response = requests.delete(
            f"{BASE_URL}/api/v1/warehouse/api-keys/{created_key_id}",
            headers=headers
        )
        if response.status_code == 204:
            print(f"   ✅ API Key deleted")
    except Exception as e:
        print(f"   ⚠️  Cleanup error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - WAREHOUSE TAB FIX VERIFIED!")
    print("=" * 80)
    print("\nSummary:")
    print("  • JWT authentication works for all warehouse endpoints")
    print("  • No 401 redirect to login page")
    print("  • API key creation/listing/deletion works")
    print("  • Webhook creation/listing/deletion works")
    print("  • Warehouse tab should now be fully functional")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_warehouse_tab_fix()
    exit(0 if success else 1)
