"""
Verification script for migration 004 - Enhanced Data Models
This script verifies that:
1. Existing products have fragile=FALSE and stackable=TRUE
2. Existing boxes have max_weight_kg=30.0 and material_type='cardboard'
3. New fields can be set when creating products/boxes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_migration():
    """Verify the migration was applied correctly"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("VERIFYING MIGRATION 004: Enhanced Data Models")
        print("=" * 60)
        
        # Check if columns exist in products table
        print("\n1. Checking products table columns...")
        result = db.execute(text("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            AND column_name IN ('fragile', 'stackable')
            ORDER BY column_name
        """))
        
        product_columns = result.fetchall()
        if len(product_columns) == 2:
            print("   ✓ Products table has 'fragile' and 'stackable' columns")
            for col in product_columns:
                print(f"     - {col[0]}: {col[1]} (default: {col[2]})")
        else:
            print("   ✗ Products table missing columns!")
            return False
        
        # Check if columns exist in boxes table
        print("\n2. Checking boxes table columns...")
        result = db.execute(text("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'boxes' 
            AND column_name IN ('max_weight_kg', 'material_type')
            ORDER BY column_name
        """))
        
        box_columns = result.fetchall()
        if len(box_columns) == 2:
            print("   ✓ Boxes table has 'max_weight_kg' and 'material_type' columns")
            for col in box_columns:
                print(f"     - {col[0]}: {col[1]} (default: {col[2]})")
        else:
            print("   ✗ Boxes table missing columns!")
            return False
        
        # Check existing products have correct defaults
        print("\n3. Checking existing products have correct default values...")
        result = db.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN fragile = false THEN 1 ELSE 0 END) as fragile_false,
                   SUM(CASE WHEN stackable = true THEN 1 ELSE 0 END) as stackable_true
            FROM products
        """))
        
        product_stats = result.fetchone()
        if product_stats:
            total = product_stats[0]
            fragile_false = product_stats[1]
            stackable_true = product_stats[2]
            
            print(f"   Total products: {total}")
            print(f"   Products with fragile=FALSE: {fragile_false}")
            print(f"   Products with stackable=TRUE: {stackable_true}")
            
            if total > 0:
                if fragile_false == total and stackable_true == total:
                    print("   ✓ All existing products have correct default values")
                else:
                    print("   ✗ Some products have incorrect default values!")
                    return False
            else:
                print("   ℹ No existing products to verify")
        
        # Check existing boxes have correct defaults
        print("\n4. Checking existing boxes have correct default values...")
        result = db.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN max_weight_kg = 30.0 THEN 1 ELSE 0 END) as max_weight_30,
                   SUM(CASE WHEN material_type = 'cardboard' THEN 1 ELSE 0 END) as material_cardboard
            FROM boxes
        """))
        
        box_stats = result.fetchone()
        if box_stats:
            total = box_stats[0]
            max_weight_30 = box_stats[1]
            material_cardboard = box_stats[2]
            
            print(f"   Total boxes: {total}")
            print(f"   Boxes with max_weight_kg=30.0: {max_weight_30}")
            print(f"   Boxes with material_type='cardboard': {material_cardboard}")
            
            if total > 0:
                if max_weight_30 == total and material_cardboard == total:
                    print("   ✓ All existing boxes have correct default values")
                else:
                    print("   ✗ Some boxes have incorrect default values!")
                    return False
            else:
                print("   ℹ No existing boxes to verify")
        
        print("\n" + "=" * 60)
        print("✓ MIGRATION 004 VERIFICATION PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
