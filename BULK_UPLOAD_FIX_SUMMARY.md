# Bulk Upload "200 Failed" Issue - Fix Summary

## Problem
When uploading a bulk orders CSV file, you're seeing:
```
Bulk upload processed: 0 orders queued, 200 failed
```

## Root Cause
All 200 orders failed validation. The two most common reasons are:

### 1. Wrong CSV Column Names ❌
Your CSV might have columns like:
- `Order Number` instead of `order_number`
- `Customer Name` instead of `customer_name`
- `SKU` instead of `product_sku`
- `Qty` instead of `quantity`

**Required column names (exact, case-sensitive):**
```
order_number,customer_name,product_sku,quantity
```

### 2. Product SKUs Don't Exist ❌
The `product_sku` values in your CSV don't exist in your Products database.

Example:
- CSV has: `WIDGET-123`
- Database has: `PROD-001`, `PROD-002`, `PROD-003`
- Result: Order fails with "Unknown product SKUs: WIDGET-123"

## Solution

### Quick Fix Option 1: Use Our Sample File
1. Make sure you have products with SKUs: `PROD-001`, `PROD-002`, `PROD-003`
2. Upload `sample_data/bulk_orders_sample.csv`
3. Should succeed with "10 orders queued, 0 failed"

### Quick Fix Option 2: Generate CSV from Your Products
```bash
# Get your auth token from browser (F12 → Application → Local Storage → token)
python generate_bulk_orders_from_products.py YOUR_AUTH_TOKEN

# This creates my_bulk_orders.csv using your actual products
# Upload this file - it will work!
```

### Fix Your Own CSV

#### Step 1: Check Column Names
Open your CSV and verify the first line is exactly:
```
order_number,customer_name,product_sku,quantity
```

#### Step 2: Verify Product SKUs
1. Go to Products tab in PackOptima
2. Check what SKUs exist (e.g., PROD-001, PROD-002)
3. Update your CSV to use those exact SKUs

#### Step 3: Diagnose Issues
```bash
python diagnose_bulk_upload.py your_file.csv YOUR_AUTH_TOKEN
```

This will tell you exactly what's wrong.

## Correct CSV Format

```csv
order_number,customer_name,product_sku,quantity
ORD-001,John Smith,PROD-001,2
ORD-001,John Smith,PROD-002,1
ORD-002,Jane Doe,PROD-003,3
```

### Rules:
- Column names must match exactly (case-sensitive)
- All SKUs must exist in your Products database
- Quantity must be a positive integer
- Multiple rows with same order_number = one order with multiple items

## Files Created

1. **BULK_ORDER_CSV_FORMAT_GUIDE.md** - Detailed format guide
2. **sample_data/bulk_orders_sample.csv** - Working sample CSV
3. **diagnose_bulk_upload.py** - Diagnostic tool to check your CSV
4. **generate_bulk_orders_from_products.py** - Generate CSV from your products

## Testing

### Test with Sample File
```bash
# 1. Upload sample_data/bulk_orders_sample.csv
# 2. Should see: "10 orders queued, 0 failed"
```

### Test with Your File
```bash
# 1. Check format
python diagnose_bulk_upload.py your_file.csv YOUR_AUTH_TOKEN

# 2. Fix any errors shown

# 3. Upload to Bulk Upload tab

# 4. Check results
```

## Common Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Column names | `Order Number,Customer,SKU,Qty` | `order_number,customer_name,product_sku,quantity` |
| Non-existent SKU | `WIDGET-123` (doesn't exist) | `PROD-001` (exists in database) |
| Empty values | `ORD-001,,PROD-001,2` | `ORD-001,John,PROD-001,2` |
| Invalid quantity | `0`, `-1`, `2.5` | `1`, `2`, `10` |

## Need More Help?

1. Read the detailed guide: `BULK_ORDER_CSV_FORMAT_GUIDE.md`
2. Check backend logs: `docker logs packoptima-backend --tail 100`
3. Use diagnostic tool: `python diagnose_bulk_upload.py your_file.csv`
4. Generate working sample: `python generate_bulk_orders_from_products.py YOUR_TOKEN`

## Expected Success Message

When your CSV is correct, you should see:
```
Bulk upload processed: 10 orders queued, 0 failed
```

The number will match the number of unique order_number values in your CSV.
