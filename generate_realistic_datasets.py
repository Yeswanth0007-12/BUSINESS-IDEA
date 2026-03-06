"""
Generate Realistic Datasets for PackOptima
Creates 1000 products and 20 boxes with realistic data that will show savings
"""
import csv
import random

# Product categories with typical dimensions and weights
PRODUCT_TEMPLATES = [
    # Electronics
    {"category": "Electronics", "base_name": "Laptop", "length": (30, 40), "width": (20, 30), "height": (2, 5), "weight": (1.5, 3.0)},
    {"category": "Electronics", "base_name": "Monitor", "length": (50, 70), "width": (30, 50), "height": (5, 10), "weight": (3.0, 8.0)},
    {"category": "Electronics", "base_name": "Keyboard", "length": (40, 50), "width": (12, 18), "height": (2, 4), "weight": (0.5, 1.2)},
    {"category": "Electronics", "base_name": "Mouse", "length": (10, 15), "width": (6, 10), "height": (3, 5), "weight": (0.1, 0.3)},
    {"category": "Electronics", "base_name": "Webcam", "length": (8, 12), "width": (5, 8), "height": (5, 8), "weight": (0.2, 0.5)},
    {"category": "Electronics", "base_name": "USB Cable", "length": (15, 25), "width": (10, 15), "height": (2, 4), "weight": (0.1, 0.3)},
    {"category": "Electronics", "base_name": "Power Bank", "length": (12, 18), "width": (6, 10), "height": (2, 4), "weight": (0.3, 0.6)},
    {"category": "Electronics", "base_name": "Headphones", "length": (18, 25), "width": (15, 22), "height": (6, 10), "weight": (0.2, 0.5)},
    {"category": "Electronics", "base_name": "SSD Drive", "length": (10, 15), "width": (7, 10), "height": (1, 3), "weight": (0.1, 0.2)},
    {"category": "Electronics", "base_name": "Phone Case", "length": (15, 20), "width": (8, 12), "height": (1, 2), "weight": (0.05, 0.15)},
    
    # Books
    {"category": "Books", "base_name": "Hardcover Book", "length": (20, 30), "width": (15, 25), "height": (2, 5), "weight": (0.5, 1.5)},
    {"category": "Books", "base_name": "Paperback Book", "length": (18, 25), "width": (12, 18), "height": (1, 3), "weight": (0.2, 0.6)},
    {"category": "Books", "base_name": "Textbook", "length": (25, 35), "width": (20, 28), "height": (3, 6), "weight": (1.0, 2.5)},
    {"category": "Books", "base_name": "Magazine", "length": (25, 35), "width": (20, 28), "height": (0.5, 1.5), "weight": (0.2, 0.5)},
    
    # Clothing
    {"category": "Clothing", "base_name": "T-Shirt", "length": (25, 35), "width": (20, 30), "height": (2, 5), "weight": (0.15, 0.3)},
    {"category": "Clothing", "base_name": "Jeans", "length": (30, 40), "width": (25, 35), "height": (3, 6), "weight": (0.5, 0.8)},
    {"category": "Clothing", "base_name": "Jacket", "length": (40, 55), "width": (35, 50), "height": (5, 10), "weight": (0.6, 1.2)},
    {"category": "Clothing", "base_name": "Shoes", "length": (25, 35), "width": (15, 25), "height": (10, 15), "weight": (0.5, 1.0)},
    {"category": "Clothing", "base_name": "Socks", "length": (15, 25), "width": (10, 15), "height": (2, 4), "weight": (0.05, 0.15)},
    
    # Toys
    {"category": "Toys", "base_name": "Action Figure", "length": (15, 25), "width": (10, 18), "height": (5, 10), "weight": (0.1, 0.4)},
    {"category": "Toys", "base_name": "Board Game", "length": (25, 40), "width": (25, 40), "height": (5, 10), "weight": (0.5, 1.5)},
    {"category": "Toys", "base_name": "Puzzle", "length": (30, 45), "width": (20, 35), "height": (3, 6), "weight": (0.4, 1.0)},
    {"category": "Toys", "base_name": "Stuffed Animal", "length": (20, 40), "width": (15, 30), "height": (15, 30), "weight": (0.2, 0.8)},
    
    # Fragile
    {"category": "Fragile", "base_name": "Glass Vase", "length": (15, 25), "width": (15, 25), "height": (20, 35), "weight": (0.5, 1.5)},
    {"category": "Fragile", "base_name": "Ceramic Mug", "length": (10, 15), "width": (10, 15), "height": (10, 15), "weight": (0.3, 0.6)},
    {"category": "Fragile", "base_name": "Picture Frame", "length": (20, 40), "width": (15, 30), "height": (2, 5), "weight": (0.5, 1.5)},
]

# Box sizes (realistic packaging options)
BOX_SIZES = [
    {"name": "Tiny Box", "length_cm": 15, "width_cm": 10, "height_cm": 8, "cost_per_unit": 0.80},
    {"name": "Extra Small Box", "length_cm": 20, "width_cm": 15, "height_cm": 10, "cost_per_unit": 1.20},
    {"name": "Small Box", "length_cm": 25, "width_cm": 20, "height_cm": 15, "cost_per_unit": 1.80},
    {"name": "Small-Medium Box", "length_cm": 30, "width_cm": 25, "height_cm": 20, "cost_per_unit": 2.50},
    {"name": "Medium Box", "length_cm": 40, "width_cm": 30, "height_cm": 25, "cost_per_unit": 3.50},
    {"name": "Medium-Large Box", "length_cm": 50, "width_cm": 35, "height_cm": 30, "cost_per_unit": 4.50},
    {"name": "Large Box", "length_cm": 60, "width_cm": 40, "height_cm": 35, "cost_per_unit": 5.50},
    {"name": "Extra Large Box", "length_cm": 70, "width_cm": 50, "height_cm": 40, "cost_per_unit": 7.00},
    {"name": "Jumbo Box", "length_cm": 80, "width_cm": 60, "height_cm": 50, "cost_per_unit": 9.00},
    {"name": "Mega Box", "length_cm": 100, "width_cm": 70, "height_cm": 60, "cost_per_unit": 12.00},
    
    # Specialized boxes
    {"name": "Flat Small", "length_cm": 35, "width_cm": 25, "height_cm": 5, "cost_per_unit": 2.00},
    {"name": "Flat Medium", "length_cm": 50, "width_cm": 35, "height_cm": 5, "cost_per_unit": 3.00},
    {"name": "Flat Large", "length_cm": 70, "width_cm": 50, "height_cm": 5, "cost_per_unit": 4.50},
    {"name": "Tall Narrow", "length_cm": 20, "width_cm": 20, "height_cm": 40, "cost_per_unit": 3.50},
    {"name": "Cube Small", "length_cm": 25, "width_cm": 25, "height_cm": 25, "cost_per_unit": 2.80},
    {"name": "Cube Medium", "length_cm": 35, "width_cm": 35, "height_cm": 35, "cost_per_unit": 4.20},
    {"name": "Cube Large", "length_cm": 50, "width_cm": 50, "height_cm": 50, "cost_per_unit": 6.50},
    {"name": "Document Box", "length_cm": 35, "width_cm": 25, "height_cm": 10, "cost_per_unit": 2.20},
    {"name": "Shoe Box", "length_cm": 35, "width_cm": 25, "height_cm": 15, "cost_per_unit": 2.50},
    {"name": "Apparel Box", "length_cm": 45, "width_cm": 35, "height_cm": 10, "cost_per_unit": 3.20},
]

def generate_products(count=1000):
    """Generate realistic product data"""
    products = []
    
    for i in range(1, count + 1):
        # Select random template
        template = random.choice(PRODUCT_TEMPLATES)
        
        # Generate dimensions within template range
        length = round(random.uniform(*template["length"]), 1)
        width = round(random.uniform(*template["width"]), 1)
        height = round(random.uniform(*template["height"]), 1)
        weight = round(random.uniform(*template["weight"]), 2)
        
        # Generate monthly order volume (realistic distribution)
        volume_tier = random.choices(
            [50, 100, 200, 500, 1000],
            weights=[30, 40, 20, 8, 2]
        )[0]
        monthly_volume = random.randint(int(volume_tier * 0.8), int(volume_tier * 1.2))
        
        # Create product
        product = {
            "name": f"{template['base_name']} {i:04d}",
            "sku": f"{template['category'][:3].upper()}-{i:04d}",
            "category": template["category"],
            "length_cm": length,
            "width_cm": width,
            "height_cm": height,
            "weight_kg": weight,
            "monthly_order_volume": monthly_volume
        }
        
        products.append(product)
    
    return products

def generate_boxes():
    """Generate box data"""
    return BOX_SIZES

def save_csv(filename, data, fieldnames):
    """Save data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Generate datasets
print("Generating realistic datasets...")
print("="*80)

# Generate products
products = generate_products(1000)
product_fieldnames = ["name", "sku", "category", "length_cm", "width_cm", "height_cm", "weight_kg", "monthly_order_volume"]
save_csv("realistic_products_1000.csv", products, product_fieldnames)
print(f"✓ Generated realistic_products_1000.csv")
print(f"  - 1000 products")
print(f"  - Categories: Electronics, Books, Clothing, Toys, Fragile")
print(f"  - Realistic dimensions and weights")
print(f"  - Monthly volumes: 40-1200 orders")

# Generate boxes
boxes = generate_boxes()
box_fieldnames = ["name", "length_cm", "width_cm", "height_cm", "cost_per_unit"]
save_csv("realistic_boxes_20.csv", boxes, box_fieldnames)
print(f"\n✓ Generated realistic_boxes_20.csv")
print(f"  - 20 different box sizes")
print(f"  - Costs: $0.80 - $12.00 per unit")
print(f"  - Various shapes: standard, flat, tall, cube")

# Statistics
print("\n" + "="*80)
print("DATASET STATISTICS")
print("="*80)

# Product statistics
categories = {}
for p in products:
    cat = p["category"]
    categories[cat] = categories.get(cat, 0) + 1

print("\nProducts by Category:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count} products")

# Size distribution
small = sum(1 for p in products if p["length_cm"] <= 20 and p["width_cm"] <= 15)
medium = sum(1 for p in products if 20 < p["length_cm"] <= 40 and 15 < p["width_cm"] <= 30)
large = sum(1 for p in products if p["length_cm"] > 40 or p["width_cm"] > 30)

print(f"\nProducts by Size:")
print(f"  Small (≤20x15 cm): {small}")
print(f"  Medium (20-40x15-30 cm): {medium}")
print(f"  Large (>40x30 cm): {large}")

# Volume distribution
low_vol = sum(1 for p in products if p["monthly_order_volume"] < 100)
med_vol = sum(1 for p in products if 100 <= p["monthly_order_volume"] < 300)
high_vol = sum(1 for p in products if p["monthly_order_volume"] >= 300)

print(f"\nProducts by Monthly Volume:")
print(f"  Low (<100): {low_vol}")
print(f"  Medium (100-300): {med_vol}")
print(f"  High (≥300): {high_vol}")

print("\n" + "="*80)
print("FILES CREATED:")
print("="*80)
print("  1. realistic_products_1000.csv - Ready to upload")
print("  2. realistic_boxes_20.csv - Ready to upload")
print("\nThese datasets will show REAL SAVINGS because:")
print("  ✓ Products have varied sizes")
print("  ✓ Boxes have different costs")
print("  ✓ Optimization will find cheaper boxes that fit")
print("  ✓ High monthly volumes amplify savings")
print("="*80)
