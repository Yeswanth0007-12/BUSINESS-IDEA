"""
Simple test to verify migration 004 worked correctly
Tests database directly and via SQL queries
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

def test_migration():
    """Test the migration"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("TESTING MIGRATION 004")
        print("=" * 60)
        
        # Test 1: Verify columns exist
        print("\n1. Verifying new columns exist...")
        result = db.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'products' 
            AND column_name IN ('fragile', 'stackable')
        """))
        product_cols = [row[0] for row in result.fetchall()]
        
        result = db.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'boxes' 
            AND column_name IN ('max_weight_kg', 'material_type')
        """))
        box_cols = [row[0] for row in result.fetchall()]
        
        if len(product_cols) == 2 and len(box_cols) == 2:
            print("   ✓ All new columns exist")
        else:
            print(f"   ✗ Missing columns! Products: {product_cols}, Boxes: {box_cols}")
            return False
        
        # Test 2: Insert product without new fields (should use defaults)
        print("\n2. Testing product creation without new fields...")
        result = db.execute(text("""
            INSERT INTO products (company_id, name, sku, category, length_cm, width_cm, height_cm, weight_kg, monthly_order_volume, created_at)
            VALUES (1, 'Test Product', 'TEST-MIGRATION-001', 'test', 10.0, 10.0, 10.0, 1.0, 100, NOW())
            RETURNING id, fragile, stackable
        """))
        db.commit()
        
        row = result.fetchone()
        if row and row[1] == False and row[2] == True:
            print(f"   ✓ Product created with defaults: fragile={row[1]}, stackable={row[2]}")
        else:
            print(f"   ✗ Defaults not applied correctly: {row}")
            return False
        
        # Test 3: Insert product with new fields
        print("\n3. Testing product creation with new fields...")
        result = db.execute(text("""
            INSERT INTO products (company_id, name, sku, category, length_cm, width_cm, height_cm, weight_kg, monthly_order_volume, fragile, stackable, created_at)
            VALUES (1, 'Test Product 2', 'TEST-MIGRATION-002', 'test', 10.0, 10.0, 10.0, 1.0, 100, TRUE, FALSE, NOW())
            RETURNING id, fragile, stackable
        """))
        db.commit()
        
        row = result.fetchone()
        if row and row[1] == True and row[2] == False:
            print(f"   ✓ Product created with custom values: fragile={row[1]}, stackable={row[2]}")
        else:
            print(f"   ✗ Custom values not set correctly: {row}")
            return False
        
        # Test 4: Insert box without new fields (should use defaults)
        print("\n4. Testing box creation without new fields...")
        result = db.execute(text("""
            INSERT INTO boxes (company_id, name, length_cm, width_cm, height_cm, cost_per_unit, usage_count, created_at)
            VALUES (1, 'Test Box', 20.0, 20.0, 20.0, 0.5, 0, NOW())
            RETURNING id, max_weight_kg, material_type
        """))
        db.commit()
        
        row = result.fetchone()
        if row and row[1] == 30.0 and row[2] == 'cardboard':
            print(f"   ✓ Box created with defaults: max_weight_kg={row[1]}, material_type={row[2]}")
        else:
            print(f"   ✗ Defaults not applied correctly: {row}")
            return False
        
        # Test 5: Insert box with new fields
        print("\n5. Testing box creation with new fields...")
        result = db.execute(text("""
            INSERT INTO boxes (company_id, name, length_cm, width_cm, height_cm, cost_per_unit, usage_count, max_weight_kg, material_type, created_at)
            VALUES (1, 'Test Box 2', 20.0, 20.0, 20.0, 0.75, 0, 50.0, 'plastic', NOW())
            RETURNING id, max_weight_kg, material_type
        """))
        db.commit()
        
        row = result.fetchone()
        if row and row[1] == 50.0 and row[2] == 'plastic':
            print(f"   ✓ Box created with custom values: max_weight_kg={row[1]}, material_type={row[2]}")
        else:
            print(f"   ✗ Custom values not set correctly: {row}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ ALL MIGRATION TESTS PASSED")
        print("=" * 60)
        print("\nSummary:")
        print("- Database columns added successfully")
        print("- Default values work correctly")
        print("- Custom values can be set")
        print("- Backward compatibility maintained")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_migration()
    sys.exit(0 if success else 1)
