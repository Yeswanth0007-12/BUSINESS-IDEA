"""
Auto-assign current boxes to products that don't have them.

This script:
1. Finds all products without current_box_id
2. For each product, finds suitable boxes
3. Assigns an OVERSIZED box (to create savings opportunity)
4. Updates the database

Run this AFTER uploading products and boxes via CSV.
"""

import sys
import os
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.product import Product
from app.models.box import Box
from app.core.database import get_db

# Database connection
DATABASE_URL = "postgresql://packoptima:packoptima123@localhost:5432/packoptima"


def find_suitable_boxes(product, boxes, padding=2.0):
    """Find all boxes that can fit the product with padding."""
    required_length = product.length_cm + (2 * padding)
    required_width = product.width_cm + (2 * padding)
    required_height = product.height_cm + (2 * padding)
    
    suitable = []
    for box in boxes:
        # Check if product fits in any orientation
        product_dims = sorted([required_length, required_width, required_height])
        box_dims = sorted([box.length_cm, box.width_cm, box.height_cm])
        
        if all(p <= b for p, b in zip(product_dims, box_dims)):
            suitable.append(box)
    
    return suitable


def assign_oversized_box(suitable_boxes):
    """
    Assign an oversized/expensive box to simulate real-world inefficiency.
    
    Strategy:
    - 70% chance: Pick from upper 50% of boxes (oversized)
    - 30% chance: Pick from upper 25% (very oversized)
    """
    if not suitable_boxes:
        return None
    
    # Sort by cost (ascending)
    sorted_boxes = sorted(suitable_boxes, key=lambda b: b.cost_per_unit)
    
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


def main():
    """Auto-assign current boxes to products."""
    print("🚀 Auto-assigning current boxes to products...\n")
    
    # Create database session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get all products without current_box_id
        products_without_box = db.query(Product).filter(Product.current_box_id == None).all()
        print(f"📦 Found {len(products_without_box)} products without current box")
        
        if not products_without_box:
            print("✅ All products already have current boxes assigned!")
            return
        
        # Get all boxes (grouped by company)
        companies = set(p.company_id for p in products_without_box)
        
        total_assigned = 0
        total_skipped = 0
        
        for company_id in companies:
            print(f"\n🏢 Processing Company ID: {company_id}")
            
            # Get boxes for this company
            boxes = db.query(Box).filter(Box.company_id == company_id).all()
            print(f"   Available boxes: {len(boxes)}")
            
            if not boxes:
                print(f"   ⚠️  No boxes found for company {company_id}")
                continue
            
            # Get products for this company
            company_products = [p for p in products_without_box if p.company_id == company_id]
            print(f"   Products to assign: {len(company_products)}")
            
            assigned = 0
            skipped = 0
            
            for product in company_products:
                # Find suitable boxes
                suitable_boxes = find_suitable_boxes(product, boxes)
                
                if not suitable_boxes:
                    print(f"   ⚠️  No suitable box for: {product.name}")
                    skipped += 1
                    continue
                
                # Assign oversized box
                current_box = assign_oversized_box(suitable_boxes)
                
                if current_box:
                    product.current_box_id = current_box.id
                    assigned += 1
                    
                    if assigned <= 5:  # Show first 5 examples
                        print(f"   ✅ {product.name} → {current_box.name} (${current_box.cost_per_unit})")
            
            print(f"   📊 Assigned: {assigned}, Skipped: {skipped}")
            total_assigned += assigned
            total_skipped += skipped
        
        # Commit changes
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ ASSIGNMENT COMPLETE")
        print(f"{'='*60}")
        print(f"Total products assigned: {total_assigned}")
        print(f"Total products skipped: {total_skipped}")
        print(f"\n💡 Next steps:")
        print(f"   1. Go to Optimize page")
        print(f"   2. Click 'Run Optimization'")
        print(f"   3. You should now see REAL savings!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
