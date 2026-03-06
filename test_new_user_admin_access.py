"""
Test New User Admin Access
Verifies that newly registered users automatically get ADMIN role
"""
import requests
import random
import string

BASE_URL = "http://localhost:8000"

def random_email():
    """Generate random email for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"

def test_new_user_admin_access():
    """Test that new users get admin role automatically"""
    print("\n" + "="*70)
    print("  TEST: New User Admin Access")
    print("="*70 + "\n")
    
    # Register new user
    email = random_email()
    register_data = {
        "email": email,
        "password": "testpass123",
        "company_name": f"Test Company {random.randint(1000, 9999)}"
    }
    
    print(f"1. Registering new user: {email}")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code not in [200, 201]:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print(f"✓ User registered successfully")
    
    # Test admin access - list users
    headers = {"Authorization": f"Bearer {token}"}
    print("\n2. Testing admin access (list users)")
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✓ Admin access granted! Found {len(users)} user(s)")
        for user in users:
            print(f"   - {user['email']} (Role: {user.get('role', 'N/A')})")
        return True
    elif response.status_code == 403:
        print(f"✗ Admin access DENIED (403 Forbidden)")
        print(f"   This means the user doesn't have ADMIN role")
        return False
    else:
        print(f"✗ Unexpected error: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_new_user_admin_access()
    
    print("\n" + "="*70)
    if success:
        print("  ✓ TEST PASSED: New users get ADMIN role automatically")
    else:
        print("  ✗ TEST FAILED: New users don't have ADMIN access")
    print("="*70 + "\n")
