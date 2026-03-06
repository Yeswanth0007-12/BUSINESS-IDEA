"""
Generate realistic products dataset with current boxes assigned to show savings.

This script creates:
1. 20 box sizes (small to large, cheap to expensive)
2. 1000 products with realistic dimensions
3. Each product is assigned a CURRENT box (usually oversized/expensive)
4. Optimization will find cheaper alternatives and show real savings

Strategy:
- Assign products to boxes that are TOO LARGE for them
- This simulates real-world scenario where companies use generic boxes
- Optimization will recommend smaller, cheaper boxes
- Result: Real cost savings displayed
"""

import csv
import random
from typing import List, Dict

# Box definitions (same as before)
BOX_SIZES = [
    {"name": "Tiny Box", "length_cm": 10, "width_cm": 8, "height_cm": 5, "cost_per_unit": 0.80},
    {"name": "Small Envelope", "length_cm": 15, "width_cm": 12, "height_cm": 3, "cost_per_unit": 0.90},
    {"name": "Small Box", "length_cm": 20, "width_cm": 15, "height_cm": 10, "cost_per_unit": 1.20},
    {"name": "Medium Flat", "length_cm": 25, "width_cm": 20, "height_cm": 8, "cost_per_unit": 1.50},
    {"name": "Medium Box", "length_cm": 30, "width_cm": 25, "height_cm": 20, "cost_per_unit": 2.00},
    {"name": "Medium Plus", "length_cm": 35, "width_cm": 30, "height_cm": 25, "cost_per_unit": 2.50},
    {"name": "Large Flat", "length_cm": 40, "width_cm": 35, "height_cm": 15, "cost_per_unit": 2.80},
    {"name": "Large Box", "length_cm": 45, "width_cm": 40, "height_cm": 35, "cost_per_unit": 3.50},
    {"name": "Large Plus", "length_cm": 50, "width_cm": 45, "height_cm": 40, "cost_per_unit": 4.20},
    {"name": "XL Flat", "length_cm": 55, "width_cm": 50, "height_cm": 20, "cost_per_unit": 4.50},
    {"name": "XL Box", "length_cm": 60, "width_cm": 55, "height_cm": 50, "cost_per_unit": 5.50},
    {"name": "XL Plus", "length_cm": 65, "width_cm": 60, "height_cm": 55, "cost_per_unit": 6.50},
    {"name": "XXL Flat", "length_cm": 70, "width_cm": 65, "height_cm": 25, "cost_per_unit": 7.00},
    {"name": "XXL Box", "length_cm": 75, "width_cm": 70, "height_cm": 65, "cost_per_unit": 8.50},
    {"name": "Jumbo Flat", "length_cm": 80, "width_cm": 75, "height_cm": 30, "cost_per_unit": 9.00},
    {"name": "Jumbo Box", "length_cm": 85, "width_cm": 80, "height_cm": 75, "cost_per_unit": 10.50},
    {"name": "Giant Flat", "length_cm": 90, "width_cm": 85, "height_cm": 35, "cost_per_unit": 11.00},
    {"name": "Giant Box", "length_cm": 95, "width_cm": 90, "height_cm": 85, "cost_per_unit": 12.00},
    {"name": "Mega Flat", "length_cm": 100, "width_cm": 95, "height_cm": 40, "cost_per_unit": 13.50},
    {"name": "Mega Box", "length_cm": 105, "width_cm": 100, "height_cm": 95, "cost_per_unit": 15.00},
]

# Product categories with typical size ranges
PRODUCT_CATEGORIES = {
    "Electronics": {
        "items": ["Smartphone", "Tablet", "Laptop", "Headphones", "Smartwatch", "Camera", "Speaker", "Router", "Keyboard", "Mouse"],
        "size_range": (5, 40),  # cm
        "weight_range": (0.1, 3.0),  # kg
        "volume_range": (100, 5000)  # monthly orders
    },
    "Books": {
        "items": ["Novel", "Textbook", "Magazine", "Comic Book", "Art Book", "Cookbook", "Dictionary", "Atlas", "Journal", "Notebook"],
        "size_range": (15, 35),
        "weight_range": (0.2, 2.5),
        "volume_range": (50, 2000)
    },
    "Clothing": {
        "items": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Shoes", "Hat", "Scarf", "Socks", "Belt"],
        "size_range": (20, 45),
        "weight_range": (0.1, 1.5),
        "volume_range": (200, 8000)
    },
    "Toys": {
        "items": ["Action Figure", "Puzzle", "Board Game", "Doll", "Building Blocks", "RC Car", "Stuffed Animal", "Ball", "Card Game", "Model Kit"],
        "size_range": (10, 50),
        "weight_range": (0.1, 2.0),
        "volume_range": (100, 3000)
    },
    "Fragile": {
        "items": ["Glass Vase", "Ceramic Mug", "Wine Bottle", "Picture Frame", "Mirror", "Lamp", "Ornament", "Dish Set", "Crystal", "Glassware"],
        "size_range": (10, 45),
        "weight_range": (0.3, 3.5),
        "volume_range": (50, 1500)
    }
}


def find_suitable_boxes(product_length: float, product_width: float, product_height: float, 
                       padding: float = 2.0) -> List[Dict]:
    """Find all boxes that can fit the product with padding."""
    required_length = product_length + (2 * padding)
    required_width = product_width + (2 * padding)
    required_height = product_height + (2 * padding)
    
    suitable = []
    for box in BOX_SIZES:
        # Check if product fits in any orientation
        product_dims = sorted([required_length, required_width, required_height])
        box_dims = sorted([box["length_cm"], box["width_cm"], box["height_cm"]])
        
        if all(p <= b for p, b in zip(product_dims, box_dims)):
            suitable.append(box)
    
    return suitable


def assign_oversized_box(suitable_boxes: List[Dict]) -> Dict:
    """
    Assign an oversized/expensive box to simulate real-world inefficiency.
    
    Strategy:
    - 70% chance: Pick a box from upper 50% of suitable boxes (oversized)
    - 30% chance: Pick a box from upper 25% (very oversized)
    
    This ensures optimization will find savings.
    """
    if not suitable_boxes:
        return None
    
    # Sort by cost (ascending)
    sorted_boxes = sorted(suitable_boxes, key=lambda b: b["cost_per_unit"])
    
    # Pick from expensive half
    if random.random() < 0.7:
        # Upper 50% (oversized)
        start_idx = len(sorted_boxes) // 2
        return random.choice(sorted_boxes[start_idx:])
    else:
        # Upper 25% (very oversized)
        start_idx = (len(sorted_boxes) * 3) // 4
        if start_idx >= len(sorted_boxes):
            start_idx = len(sorted_boxes) - 1
        return random.choice(sorted_boxes[start_idx:])


def generate_products_with_boxes(num_products: int = 1000) -> List[Dict]:
    """Generate products with current boxes assigned."""
    products = []
    
    for i in range(num_products):
        # Select random category
        category = random.choice(list(PRODUCT_CATEGORIES.keys()))
        cat_data = PRODUCT_CATEGORIES[category]
        
        # Generate product name
        item_name = random.choice(cat_data["items"])
        product_name = f"{item_name} {random.choice(['Pro', 'Plus', 'Deluxe', 'Standard', 'Premium', 'Classic', 'Elite', 'Basic'])}"
        
        # Generate SKU
        sku = f"{category[:3].upper()}-{random.randint(10000, 99999)}"
        
        # Generate dimensions within category range
        size_min, size_max = cat_data["size_range"]
        length = round(random.uniform(size_min, size_max), 1)
        width = round(random.uniform(size_min * 0.6, size_max * 0.8), 1)
        height = round(random.uniform(size_min * 0.4, size_max * 0.6), 1)
        
        # Generate weight
        weight_min, weight_max = cat_data["weight_range"]
        weight = round(random.uniform(weight_min, weight_max), 2)
        
        # Generate monthly order volume
        vol_min, vol_max = cat_data["volume_range"]
        monthly_volume = random.randint(vol_min, vol_max)
        
        # Find suitable boxes
        suitable_boxes = find_suitable_boxes(length, width, height)
        
        if not suitable_boxes:
            # Product too large for any box - skip
            continue
        
        # Assign an oversized box (to create savings opportunity)
        current_box = assign_oversized_box(suitable_boxes)
        
        products.append({
            "name": product_name,
            "sku": sku,
            "category": category,
            "length_cm": length,
            "width_cm": width,
            "height_cm": height,
            "weight_kg": weight,
            "monthly_order_volume": monthly_volume,
            "current_box_name": current_box["name"]  # For reference only
        })
    
    return products


def save_boxes_csv(filename: str = "boxes_with_savings.csv"):
    """Save boxes to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "length_cm", "width_cm", "height_cm", "cost_per_unit"])
        writer.writeheader()
        writer.writerows(BOX_SIZES)
    print(f"✅ Created {filename} with {len(BOX_SIZES)} boxes")


def save_products_csv(products: List[Dict], filename: str = "products_with_savings.csv"):
    """Save products to CSV (without current_box_name - that's just for our reference)."""
    # Remove current_box_name before saving (it's not a valid field for upload)
    products_for_csv = []
    for p in products:
        p_copy = p.copy()
        p_copy.pop("current_box_name", None)
        products_for_csv.append(p_copy)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["name", "sku", "category", "length_cm", "width_cm", "height_cm", "weight_kg", "monthly_order_volume"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products_for_csv)
    print(f"✅ Created {filename} with {len(products)} products")


def main():
    """Generate realistic datasets with savings potential."""
    print("🚀 Generating realistic datasets with savings potential...\n")
    
    # Generate boxes
    save_boxes_csv()
    
    # Generate products with current boxes
    products = generate_products_with_boxes(1000)
    save_products_csv(products)
    
    print(f"\n📊 Summary:")
    print(f"   - Boxes: 20 sizes from $0.80 to $15.00")
    print(f"   - Products: {len(products)} with realistic dimensions")
    print(f"   - Strategy: Products assigned to OVERSIZED boxes")
    print(f"   - Expected: Optimization will find cheaper alternatives")
    print(f"\n⚠️  IMPORTANT NEXT STEPS:")
    print(f"   1. Upload boxes_with_savings.csv FIRST")
    print(f"   2. Upload products_with_savings.csv SECOND")
    print(f"   3. Go to Products page and MANUALLY assign current boxes to products")
    print(f"   4. Run optimization to see REAL savings")
    print(f"\n💡 Why manual assignment?")
    print(f"   - CSV upload doesn't support current_box_id field")
    print(f"   - You need to assign boxes through the UI")
    print(f"   - Or we need to create a database script to auto-assign")


if __name__ == "__main__":
    main()
