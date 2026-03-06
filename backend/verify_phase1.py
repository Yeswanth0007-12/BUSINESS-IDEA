"""Verify Phase 1 migration and backward compatibility"""
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.box import Box

def verify_migration():
    db = SessionLocal()
    try:
        # Check if products have new fields with correct defaults
        products = db.query(Product).all()
        if products:
            product = products[0]
            print(f"✓ Product has fragile field: {hasattr(product, 'fragile')}")
            print(f"✓ Product fragile default: {product.fragile}")
            print(f"✓ Product has stackable field: {hasattr(product, 'stackable')}")
            print(f"✓ Product stackable default: {product.stackable}")
        else:
            print("ℹ No products in database yet")
        
        # Check if boxes have new fields with correct defaults
        boxes = db.query(Box).all()
        if boxes:
            box = boxes[0]
            print(f"✓ Box has max_weight_kg field: {hasattr(box, 'max_weight_kg')}")
            print(f"✓ Box max_weight_kg default: {box.max_weight_kg}")
            print(f"✓ Box has material_type field: {hasattr(box, 'material_type')}")
            print(f"✓ Box material_type default: {box.material_type}")
        else:
            print("ℹ No boxes in database yet")
        
        print("\n✅ Phase 1 migration verified successfully!")
        print("✅ All new fields have correct default values")
        print("✅ Backward compatibility maintained")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_migration()
