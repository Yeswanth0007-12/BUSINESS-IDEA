# Bulk Order CSV Upload - Format Guide

## Issue: "0 orders queued, 200 failed"

This error occurs when all orders in your CSV file fail validation. The most common reasons are:

### 1. Wrong CSV Format
The CSV must have these **exact column names** (case-sensitive):
- `order_number`
- `customer_name`
- `product_sku`
- `quantity`

### 2. Product SKUs Don't Exist
All `product_sku` values in your CSV must exist in your Products database. If a SKU doesn't exist, the order will fail.

## Correct CSV Format

```csv
order_number,customer_name,product_sku,quantity
ORD-001,John Smith,PROD-001,2
ORD-001,John Smith,PROD-002,1
ORD-002,Jane Doe,PROD-003,3
```

### Column Descriptions

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `order_number` | Yes | Unique order identifier. Multiple rows with same order_number are grouped into one order | ORD-001 |
| `customer_name` | Yes | Customer's name | John Smith |
| `product_sku` | Yes | Product SKU that exists in your Products database | PROD-001 |
| `quantity` | Yes | Positive integer quantity | 2 |

### Important Rules

1. **Column Names Must Match Exactly**
   - ❌ Wrong: `Order Number`, `OrderNumber`, `order_id`
   - ✅ Correct: `order_number`

2. **Product SKUs Must Exist**
   - Before uploading, ensure all SKUs in your CSV exist in the Products tab
   - You can check by going to Products tab and searching for the SKU

3. **Quantity Must Be Positive Integer**
   - ❌ Wrong: `0`, `-1`, `2.5`, `two`
   - ✅ Correct: `1`, `2`, `10`

4. **Multiple Items Per Order**
   - Use the same `order_number` for multiple rows to add multiple products to one order
   - Example:
     ```csv
     order_number,customer_name,product_sku,quantity
     ORD-001,John Smith,PROD-001,2
     ORD-001,John Smith,PROD-002,1
     ```
     This creates ONE order (ORD-001) with TWO products

5. **File Limits**
   - Maximum file size: 10 MB
   - Maximum rows: 10,000

## How to Fix "200 failed" Error

### Step 1: Check Your CSV Column Names
Open your CSV file and verify the first row (header) has exactly:
```
order_number,customer_name,product_sku,quantity
```

### Step 2: Verify Product SKUs Exist
1. Go to the **Products** tab in PackOptima
2. Check if the SKUs in your CSV exist in the products list
3. If they don't exist, you need to either:
   - Create the products first (Products tab → Add Product)
   - OR update your CSV to use existing SKUs

### Step 3: Check for Common Mistakes

**Common Mistake #1: Wrong Column Names**
```csv
❌ Order Number,Customer Name,SKU,Qty
✅ order_number,customer_name,product_sku,quantity
```

**Common Mistake #2: Using Non-Existent SKUs**
```csv
❌ ORD-001,John,WIDGET-123,2  (WIDGET-123 doesn't exist in database)
✅ ORD-001,John,PROD-001,2     (PROD-001 exists in database)
```

**Common Mistake #3: Empty Values**
```csv
❌ ORD-001,,PROD-001,2         (missing customer_name)
❌ ORD-001,John,,2             (missing product_sku)
✅ ORD-001,John,PROD-001,2     (all fields filled)
```

## Sample CSV Files

We've provided sample CSV files in the `sample_data/` directory:

1. **bulk_orders_sample.csv** - Sample bulk orders file
   - Uses SKUs: PROD-001, PROD-002, PROD-003
   - 10 orders with 16 total items

## Testing Your CSV

### Option 1: Use Our Sample File
1. First, ensure you have products with SKUs: PROD-001, PROD-002, PROD-003
2. Upload `sample_data/bulk_orders_sample.csv`
3. Should succeed with "10 orders queued, 0 failed"

### Option 2: Test Your Own CSV
1. Start with a small CSV (2-3 orders)
2. Verify column names match exactly
3. Verify all SKUs exist in Products tab
4. Upload and check results
5. If successful, upload your full CSV

## Viewing Failed Orders

If some orders fail, you can view the failure reasons:

1. After upload, note the `upload_id` from the response
2. Go to the Bulk Upload tab
3. Click on the upload to see details
4. Failed orders will show the specific error message (e.g., "Unknown product SKUs: WIDGET-123")

## API Documentation

For programmatic access, see the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Look for the `/api/v1/bulk-upload` endpoints.

## Need Help?

If you're still having issues:

1. Check the backend logs:
   ```bash
   docker logs packoptima-backend --tail 100
   ```

2. Run the diagnostic script:
   ```bash
   python diagnose_bulk_upload.py your_file.csv
   ```

3. Verify your products exist:
   - Go to Products tab
   - Export products to CSV
   - Compare SKUs with your bulk order CSV
