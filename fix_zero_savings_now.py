"""
Quick fix for zero savings issue.

This script assigns current boxes to products that don't have one,
so the optimization can calculate real savings.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def fix_zero_savings(token: str):
    """Assign current boxes to products."""
    
    print("=" * 80)
    print("FIX ZERO SAVINGS - ASSIGN CURRENT BOXES")
    print("=" * 80)
    print()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Get all products
    print("Step 1: Fetching products...")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers, params={"limit": 10000})
        if response.status_code != 200:
            print(f"❌ Failed to fetch products: {response.status_code}")
            return False
        
        products = response.json()
        print(f"✅ Found {len(products)} products")
        
        if not products:
            print("❌ No products found. Please add products first.")
            return False
        
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return False
    
    # Step 2: Get all boxes
    print("\nStep 2: Fetching boxes...")
    try:
        response = requests.get(f"{BASE_URL}/boxes", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch boxes: {response.status_code}")
            return False
        
        boxes = response.json()
        print(f"✅ Found {len(boxes)} boxes")
        
        if not boxes:
            print("❌ No boxes found. Please add boxes first.")
            return False
        
    except Exception as e:
        print(f"❌ Error fetching boxes: {e}")
        return False
    
    # Step 3: Assign current boxes to products without one
    print("\nStep 3: Assigning current boxes to products...")
    print("-" * 80)
    
    products_without_box = [p for p in products if not p.get("current_box_id")]
    print(f"Found {len(products_without_box)} products without current box")
    
    if not products_without_box:
        print("✅ All products already have current boxes assigned!")
        return True
    
    # Sort boxes by cost (descending) to assign expensive boxes
    boxes_sorted = sorted(boxes, key=lambda b: b["cost_per_unit"], reverse=True)
    
    updated = 0
    skipped = 0
    
    for product in products_without_box:
        # Find a box that can fit this product
        product_volume = product["length_cm"] * product["width_cm"] * product["height_cm"]
        
        suitable_box = None
        for box in boxes_sorted:
            box_volume = box["length_cm"] * box["width_cm"] * box["height_cm"]
            
            # Check if product fits in box (simple volume check)
            if box_volume >= product_volume * 1.2:  # 20% buffer
                suitable_box = box
                break
        
        if not suitable_box:
            # If no suitable box found, use the largest box
            suitable_box = max(boxes, key=lambda b: b["length_cm"] * b["width_cm"] * b["height_cm"])
        
        # Update product with current_box_id
        try:
            update_data = {
                "sku": product["sku"],
                "name": product["name"],
                "length_cm": product["length_cm"],
                "width_cm": product["width_cm"],
                "height_cm": product["height_cm"],
                "weight_kg": product.get("weight_kg", 1.0),
                "fragile": product.get("fragile", False),
                "stackable": product.get("stackable", True),
                "current_box_id": suitable_box["id"]
            }
            
            response = requests.put(
                f"{BASE_URL}/products/{product['id']}",
                headers=headers,
                json=update_data
            )
            
            if response.status_code == 200:
                updated += 1
                print(f"  ✅ {product['sku']}: Assigned box '{suitable_box['name']}' (${suitable_box['cost_per_unit']:.2f})")
            else:
                skipped += 1
                print(f"  ⚠️  {product['sku']}: Failed to update ({response.status_code})")
                
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  {product['sku']}: Error - {e}")
    
    print()
    print("=" * 80)
    print(f"✅ COMPLETE: Updated {updated} products, skipped {skipped}")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Go to the Optimize tab")
    print("2. Click 'Run Optimization'")
    print("3. You should now see real savings (not $0.00)")
    print()
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_zero_savings_now.py <auth_token>")
        print()
        print("To get your auth token:")
        print("1. Login to PackOptima")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application/Storage → Local Storage")
        print("4. Copy the 'token' value")
        print()
        print("Example:")
        print("  python fix_zero_savings_now.py eyJhbGc...")
        print()
        sys.exit(1)
    
    token = sys.argv[1]
    success = fix_zero_savings(token)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
