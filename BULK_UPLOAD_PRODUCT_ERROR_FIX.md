# Fix: Unknown Product SKUs Error

## Problem

You're getting this error when uploading bulk orders:
```
Order: ORD-100001
Unknown product SKUs: DRONE-071. Please add these products to your catalog first.
Missing SKUs: DRONE-071
```

## Why This Happens

The bulk upload system validates that all products in your orders exist in your Products catalog BEFORE creating the orders. This prevents:
- Orders with invalid products
- Optimization failures
- Data integrity issues

## Solution

You MUST add products to your catalog BEFORE uploading orders that reference them.

---

## Quick Fix: 3 Options

### Option 1: Use Sample Data (Easiest)

**Step 1: Upload Products**
1. Go to **Products** tab
2. Click "Upload CSV" or "Import Products"
3. Select `sample_data/products_sample.csv`
4. Click Upload
5. Wait for success message

**Step 2: Upload Orders**
1. Go to **Bulk Upload** or **Orders** tab
2. Click "Upload Bulk Orders"
3. Select `sample_data/bulk_orders_with_existing_skus.csv` (NEW FILE)
4. Click Upload
5. Orders will be created successfully!

---

### Option 2: Add Missing Products Manually

**For each missing SKU (DRONE-071, SSD-601, etc.):**

1. Go to **Products** tab
2. Click "Add Product" or "+"
3. Fill in details:
   - **Name**: Drone Camera 4K (or whatever)
   - **SKU**: DRONE-071
   - **Category**: Electronics
   - **Dimensions**: Length, Width, Height (cm)
   - **Weight**: Weight (kg)
   - **Monthly Volume**: Estimated orders/month
4. Click "Save"
5. Repeat for all missing SKUs

**Then retry bulk upload**

---

### Option 3: Create CSV with Correct SKUs

**Step 1: Check Your Existing Products**
1. Go to **Products** tab
2. Note down the SKUs you have (e.g., ELEC-LAP-15, ELEC-MOU-WL)

**Step 2: Update Your Bulk Orders CSV**
Edit your CSV to use existing SKUs:
```csv
order_number,customer_name,product_sku,quantity
ORD-100001,Customer A,ELEC-LAP-15,5
ORD-100001,Customer A,ELEC-MOU-WL,10
ORD-100002,Customer B,ELEC-SSD-1TB,20
```

**Step 3: Upload Updated CSV**

---

## Available Sample Files

### Products CSV
**File**: `sample_data/products_sample.csv`
- Contains 20 products
- SKUs: ELEC-LAP-15, ELEC-MOU-WL, ELEC-SSD-1TB, etc.
- Ready to upload

### Bulk Orders CSV (Original)
**File**: `sample_data/bulk_orders_sample.csv`
- Uses SKUs: PROD-001, PROD-002, PROD-003
- ⚠️ These products don't exist yet

### Bulk Orders CSV (Fixed - NEW!)
**File**: `sample_data/bulk_orders_with_existing_skus.csv`
- Uses SKUs from products_sample.csv
- ✅ Will work immediately after uploading products
- Contains 10 orders with 25 line items

---

## Correct Upload Sequence

```
1. Upload Products First
   ↓
2. Verify Products Exist
   ↓
3. Upload Bulk Orders
   ↓
4. Success!
```

---

## CSV Format Reference

### Products CSV Format
```csv
name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Laptop 15 inch,ELEC-LAP-15,Electronics,38,27,3,2.1,450
Wireless Mouse,ELEC-MOU-WL,Electronics,12,8,4,0.12,850
```

### Bulk Orders CSV Format
```csv
order_number,customer_name,product_sku,quantity
ORD-100001,Tech Solutions Inc,ELEC-LAP-15,5
ORD-100001,Tech Solutions Inc,ELEC-MOU-WL,10
ORD-100002,Office Supplies Co,ELEC-SSD-1TB,20
```

**Important**: 
- Same `order_number` = multiple products in one order
- `product_sku` MUST match existing products

---

## Testing Your Fix

### Test 1: Upload Products
```bash
# In Docker container
docker exec -it packoptima-api python -c "
from app.core.database import SessionLocal
from app.models.product import Product
db = SessionLocal()
count = db.query(Product).count()
print(f'Products in database: {count}')
db.close()
"
```

### Test 2: Check Specific SKU
```bash
docker exec -it packoptima-api python -c "
from app.core.database import SessionLocal
from app.models.product import Product
db = SessionLocal()
product = db.query(Product).filter(Product.sku == 'ELEC-LAP-15').first()
print(f'Product found: {product.name if product else \"Not found\"}')
db.close()
"
```

---

## Common Mistakes

### ❌ Wrong: Uploading orders before products
```
1. Upload bulk_orders.csv
2. Error: Unknown SKUs
```

### ✅ Correct: Upload products first
```
1. Upload products_sample.csv
2. Upload bulk_orders_with_existing_skus.csv
3. Success!
```

---

## Need Help?

### Check Product Exists
1. Go to Products tab
2. Search for SKU (e.g., "DRONE-071")
3. If not found → Add it first

### Verify CSV Format
- No extra spaces
- Correct column names
- SKUs match exactly (case-sensitive)

### Still Getting Errors?
1. Export your current products to see available SKUs
2. Update your bulk orders CSV to use those SKUs
3. Or add the missing products manually

---

## Summary

**The error means**: Products don't exist in your catalog yet.

**The fix**: Add products BEFORE uploading orders.

**Easiest solution**: 
1. Upload `sample_data/products_sample.csv`
2. Upload `sample_data/bulk_orders_with_existing_skus.csv`
3. Done!

---

## Files Created for You

✅ **sample_data/bulk_orders_with_existing_skus.csv** (NEW)
- 10 orders
- 25 line items
- Uses SKUs from products_sample.csv
- Ready to upload after products

Use this file instead of your current bulk orders CSV!
