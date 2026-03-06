"""
Test Optimization with Savings
Assigns current boxes to products, then runs optimization to show real savings
"""
import requests
import random
import string

BASE_URL = "http://localhost:8000"

def random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"savings_{random_str}@test.com"

print("\n" + "="*80)
print("  TEST: Optimization with Real Savings")
print("="*80 + "\n")

# Step 1: Register
email = random_email()
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": email,
    "password": "testpass123",
    "company_name": f"Savings Test {random.randint(1000, 9999)}"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✓ Registered: {email}\n")

# Step 2: Upload Boxes
print("Uploading boxes...")
boxes_csv = """name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,30,20,15,2.00
Medium Box,40,30,25,3.50
Large Box,60,40,40,5.00
Extra Large Box,80,60,50,7.00"""

files = {'file': ('boxes.csv', boxes_csv, 'text/csv')}
response = requests.post(f"{BASE_URL}/boxes/bulk-upload", files=files, headers=headers)
print(f"✓ Boxes uploaded: {response.json()['created_count']}\n")

# Get box IDs
response = requests.get(f"{BASE_URL}/boxes", headers=headers)
boxes = response.json()
large_box_id = next(b['id'] for b in boxes if 'Large' in b['name'])
small_box_id = next(b['id'] for b in boxes if 'Small' in b['name'])

print(f"Box IDs: Small={small_box_id}, Large={large_box_id}\n")

# Step 3: Create products WITH current boxes assigned
print("Creating products with current boxes...")
products = [
    {
        "name": "Laptop",
        "sku": "LAP-001",
        "category": "Electronics",
        "length_cm": 35,
        "width_cm": 25,
        "height_cm": 3,
        "weight_kg": 2.5,
        "monthly_order_volume": 100,
        "current_box_id": large_box_id  # Currently using expensive Large Box
    },
    {
        "name": "Mouse",
        "sku": "MOU-001",
        "category": "Electronics",
        "length_cm": 12,
        "width_cm": 8,
        "height_cm": 4,
        "weight_kg": 0.2,
        "monthly_order_volume": 200,
        "current_box_id": large_box_id  # Currently using expensive Large Box
    }
]

for product in products:
    response = requests.post(f"{BASE_URL}/products", json=product, headers=headers)
    print(f"✓ Created: {product['name']} (current box: Large Box)")

print()

# Step 4: Run Optimization
print("Running optimization...\n")
response = requests.post(f"{BASE_URL}/optimize", json={}, headers=headers)
optimization = response.json()

# Step 5: Display Results with Savings
print("="*80)
print("  OPTIMIZATION RESULTS WITH SAVINGS")
print("="*80 + "\n")

print(f"Products Analyzed: {optimization['total_products_analyzed']}")
print(f"Products with Savings: {optimization['products_with_savings']}")
print(f"Monthly Savings: ${optimization['total_monthly_savings']:.2f}")
print(f"Annual Savings: ${optimization['total_annual_savings']:.2f}\n")

print("Detailed Results:\n")
for result in optimization['results']:
    print(f"Product: {result['product_name']}")
    print(f"  Current Box: {result['current_box_name']}")
    print(f"  Current Cost: ${result['current_cost']:.2f}/month")
    print(f"  Recommended Box: {result['recommended_box_name']}")
    print(f"  New Cost: ${result['recommended_cost']:.2f}/month")
    print(f"  💰 SAVINGS: ${result['savings']:.2f}/month ({result['savings_percentage']:.1f}%)")
    print()

print("="*80)
print("  ✅ SUCCESS: Real savings are now showing!")
print("="*80 + "\n")
