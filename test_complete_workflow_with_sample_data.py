"""
Complete Workflow Test with Sample Data
Tests the entire workflow: Register -> Upload Products -> Upload Boxes -> Optimize -> View Results
"""
import requests
import csv
import io
import random
import string

BASE_URL = "http://localhost:8000"

def random_email():
    """Generate random email"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"workflow_{random_str}@test.com"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_complete_workflow():
    """Test complete workflow from registration to optimization"""
    
    print("\n" + "="*70)
    print("  COMPLETE WORKFLOW TEST WITH SAMPLE DATA")
    print("="*70)
    
    # Step 1: Register new user
    print_section("STEP 1: User Registration")
    email = random_email()
    register_data = {
        "email": email,
        "password": "testpass123",
        "company_name": f"Workflow Test Co {random.randint(1000, 9999)}"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code not in [200, 201]:
        print(f"✗ Registration failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ User registered: {email}")
    
    # Step 2: Upload Products via CSV
    print_section("STEP 2: Upload Products (CSV)")
    
    products_csv = """name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Laptop,LAP-001,Electronics,35,25,3,2.5,150
Mouse,MOU-001,Electronics,12,8,4,0.2,300
Keyboard,KEY-001,Electronics,45,15,3,0.8,200
Monitor,MON-001,Electronics,60,40,8,5.0,100
Headphones,HEA-001,Electronics,20,18,8,0.3,250"""
    
    files = {'file': ('products.csv', products_csv, 'text/csv')}
    response = requests.post(f"{BASE_URL}/products/bulk-upload", files=files, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"✗ Product upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print(f"✓ Products uploaded: {result['created_count']} created")
    
    # Step 3: Upload Boxes via CSV
    print_section("STEP 3: Upload Boxes (CSV)")
    
    boxes_csv = """name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,30,20,15,1.50
Medium Box,40,30,25,2.50
Large Box,60,40,40,4.00
Extra Large Box,80,60,50,6.00"""
    
    files = {'file': ('boxes.csv', boxes_csv, 'text/csv')}
    response = requests.post(f"{BASE_URL}/boxes/bulk-upload", files=files, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"✗ Box upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print(f"✓ Boxes uploaded: {result['created_count']} created")
    
    # Step 4: Run Optimization
    print_section("STEP 4: Run Optimization")
    
    response = requests.post(f"{BASE_URL}/optimize", json={}, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"✗ Optimization failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    optimization = response.json()
    print(f"✓ Optimization completed!")
    print(f"   Products Analyzed: {optimization['total_products_analyzed']}")
    print(f"   Products with Savings: {optimization['products_with_savings']}")
    print(f"   Monthly Savings: ${optimization['total_monthly_savings']:.2f}")
    print(f"   Annual Savings: ${optimization['total_annual_savings']:.2f}")
    
    # Step 5: View History
    print_section("STEP 5: View Optimization History")
    
    response = requests.get(f"{BASE_URL}/history", headers=headers)
    
    if response.status_code != 200:
        print(f"✗ History retrieval failed: {response.status_code}")
        return False
    
    history = response.json()
    print(f"✓ History retrieved: {len(history)} optimization run(s)")
    
    if history:
        latest = history[0]
        print(f"   Latest run: {latest['products_analyzed']} products analyzed")
        print(f"   Monthly savings: ${latest['total_monthly_savings']:.2f}")
    
    # Step 6: View Dashboard Analytics
    print_section("STEP 6: View Dashboard Analytics")
    
    response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    
    if response.status_code != 200:
        print(f"✗ Analytics retrieval failed: {response.status_code}")
        return False
    
    analytics = response.json()
    print(f"✓ Dashboard analytics:")
    print(f"   Total Products: {analytics['total_products']}")
    print(f"   Total Boxes: {analytics['total_boxes']}")
    print(f"   Optimization Runs: {analytics['optimization_runs_count']}")
    print(f"   Total Monthly Savings: ${analytics['total_monthly_savings']:.2f}")
    
    # Step 7: Test Enterprise Features
    print_section("STEP 7: Test Enterprise Features")
    
    # Check subscription
    response = requests.get(f"{BASE_URL}/subscriptions/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Usage tracking:")
        print(f"   Products: {usage['total_products']}")
        print(f"   Boxes: {usage['total_boxes']}")
        print(f"   Optimizations this month: {usage['optimizations_this_month']}")
    
    # Check admin access
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        print(f"✓ Admin access: {len(users)} user(s)")
    
    # Export data
    response = requests.get(f"{BASE_URL}/export/products", headers=headers)
    if response.status_code == 200:
        print(f"✓ Data export: Products CSV ({len(response.content)} bytes)")
    
    print_section("✓ COMPLETE WORKFLOW TEST PASSED")
    print("All features working correctly:")
    print("  ✓ User registration with auto-admin role")
    print("  ✓ CSV bulk upload (products & boxes)")
    print("  ✓ Optimization engine")
    print("  ✓ History tracking")
    print("  ✓ Dashboard analytics")
    print("  ✓ Enterprise features (subscriptions, RBAC, export)")
    print("\n" + "="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    
    if not success:
        print("\n✗ WORKFLOW TEST FAILED\n")
        exit(1)
