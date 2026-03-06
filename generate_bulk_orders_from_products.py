"""
Generate a sample bulk orders CSV using your existing products.

This script fetches your products from the database and creates
a sample bulk orders CSV that will work with your data.
"""
import requests
import csv
import random
import sys

BASE_URL = "http://localhost:8000"

def generate_bulk_orders_csv(token: str, output_file: str = "my_bulk_orders.csv", num_orders: int = 10):
    """Generate a bulk orders CSV from existing products."""
    
    print("=" * 80)
    print("BULK ORDERS CSV GENERATOR")
    print("=" * 80)
    print()
    
    # Fetch products
    print("Fetching your products from database...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers, params={"limit": 1000})
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch products: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        products = response.json()
        
        if not products:
            print("❌ No products found in your database!")
            print("   Please add some products first in the Products tab.")
            return False
        
        print(f"✅ Found {len(products)} products")
        print()
        
        # Generate orders
        print(f"Generating {num_orders} sample orders...")
        
        customer_names = [
            "John Smith", "Jane Doe", "Bob Johnson", "Alice Williams",
            "Charlie Brown", "Diana Prince", "Eve Adams", "Frank Miller",
            "Grace Lee", "Henry Ford", "Ivy Chen", "Jack Wilson",
            "Kate Martinez", "Leo Garcia", "Mary Rodriguez", "Nick Taylor"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["order_number", "customer_name", "product_sku", "quantity"])
            
            for i in range(1, num_orders + 1):
                order_number = f"ORD-{i:03d}"
                customer_name = random.choice(customer_names)
                
                # Each order has 1-4 products
                num_items = random.randint(1, min(4, len(products)))
                selected_products = random.sample(products, num_items)
                
                for product in selected_products:
                    sku = product["sku"]
                    quantity = random.randint(1, 5)
                    writer.writerow([order_number, customer_name, sku, quantity])
        
        print(f"✅ Generated {output_file}")
        print()
        print("CSV Preview:")
        print("-" * 80)
        
        # Show preview
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:11]:  # Show header + first 10 rows
                print(line.rstrip())
            if len(lines) > 11:
                print(f"... and {len(lines) - 11} more rows")
        
        print()
        print("=" * 80)
        print("✅ SUCCESS")
        print("=" * 80)
        print()
        print(f"Your bulk orders CSV has been created: {output_file}")
        print()
        print("Next steps:")
        print("1. Review the CSV file")
        print("2. Go to Bulk Upload tab in PackOptima")
        print("3. Upload the CSV file")
        print(f"4. You should see: '{num_orders} orders queued, 0 failed'")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_bulk_orders_from_products.py <auth_token> [output_file] [num_orders]")
        print()
        print("Example:")
        print("  python generate_bulk_orders_from_products.py eyJhbGc...")
        print("  python generate_bulk_orders_from_products.py eyJhbGc... my_orders.csv 20")
        print()
        print("To get your auth token:")
        print("1. Login to PackOptima")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application/Storage → Local Storage")
        print("4. Copy the 'token' value")
        print()
        sys.exit(1)
    
    token = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "my_bulk_orders.csv"
    num_orders = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    success = generate_bulk_orders_csv(token, output_file, num_orders)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
