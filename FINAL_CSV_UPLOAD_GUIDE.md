# PackOptima AI SaaS - CSV Upload Feature Guide

## 🎉 Feature Status: COMPLETE AND WORKING

All CSV upload functionality has been implemented, tested, and verified working correctly.

---

## Quick Start

### Access the Application

1. **Open your browser** and navigate to: http://localhost:8080
2. **Register** a new account or **Login** with existing credentials
3. **Navigate** to Products or Boxes page
4. **Click** the green "Bulk Upload CSV" button

---

## CSV Upload Features

### ✅ Products CSV Upload

Upload hundreds of products at once using a CSV file.

**CSV Format**:
```csv
name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Laptop Computer,LAP-001,Electronics,35,25,5,2.5,150
Wireless Mouse,MOU-001,Electronics,12,8,4,0.15,300
USB Cable,CAB-001,Accessories,15,10,2,0.05,500
```

**Field Requirements**:
- `name`: Product name (required, string)
- `sku`: Stock Keeping Unit (required, unique string)
- `category`: Product category (required, string)
- `length_cm`: Length in cm (required, > 0)
- `width_cm`: Width in cm (required, > 0)
- `height_cm`: Height in cm (required, > 0)
- `weight_kg`: Weight in kg (required, > 0)
- `monthly_order_volume`: Monthly orders (required, >= 0)

### ✅ Boxes CSV Upload

Upload hundreds of box sizes at once using a CSV file.

**CSV Format**:
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
Medium Box,35,25,15,2.50
Large Box,50,40,20,3.50
```

**Field Requirements**:
- `name`: Box name (required, string)
- `length_cm`: Length in cm (required, > 0)
- `width_cm`: Width in cm (required, > 0)
- `height_cm`: Height in cm (required, > 0)
- `cost_per_unit`: Cost in dollars (required, > 0)

---

## How to Use

### Step 1: Prepare Your CSV File

**Option A: Download Template**
1. Click "Bulk Upload CSV" button
2. Click "Download CSV Template"
3. Open the template in Excel or any spreadsheet software
4. Fill in your data
5. Save as CSV

**Option B: Create Your Own**
1. Create a new file in Excel or text editor
2. Add the header row with exact field names
3. Add your data rows
4. Save as CSV format

### Step 2: Upload CSV File

1. Click the green "Bulk Upload CSV" button
2. Click "Select CSV File" or drag and drop your file
3. Verify the file name appears
4. Click "Upload" button
5. Wait for processing (shows spinner)

### Step 3: View Results

**Success Message**:
- "Successfully uploaded X products/boxes"
- Shows count of items created

**Partial Success**:
- "X items created with Y errors"
- Check console for error details

**Error Message**:
- Shows specific error (invalid format, missing fields, etc.)
- Fix the CSV and try again

---

## Manual Entry Still Available

Don't want to use CSV? No problem!

- Click "Add Product" or "Add Box" button
- Fill in the form fields
- Click "Create"

Both methods work perfectly and can be used interchangeably.

---

## Validation Rules

### Products Validation

✅ All fields are required
✅ Dimensions must be positive numbers
✅ Weight must be positive
✅ Monthly order volume must be >= 0
✅ SKU must be unique per company

### Boxes Validation

✅ All fields are required
✅ Dimensions must be positive numbers
✅ Cost per unit must be positive

---

## Common Issues and Solutions

### Issue: "Failed to upload CSV file"

**Solutions**:
1. Check CSV format matches template exactly
2. Ensure all required fields are present
3. Verify no special characters in field names
4. Make sure file is saved as .csv (not .xlsx)

### Issue: "Some rows failed to upload"

**Solutions**:
1. Check console for specific row errors
2. Verify data types (numbers vs strings)
3. Ensure positive values for dimensions/costs
4. Check for duplicate SKUs (products only)

### Issue: CSV template download not working

**Solutions**:
1. Check browser popup blocker
2. Try different browser
3. Manually create CSV with correct headers

---

## Testing

### Automated Test

Run the comprehensive test suite:

```bash
python test_csv_upload.py
```

**Test Coverage**:
- ✅ Authentication (register/login)
- ✅ Products CSV upload (5 items)
- ✅ Boxes CSV upload (5 items)
- ✅ Data verification
- ✅ Error handling

### Manual Testing

1. **Test Products Upload**:
   - Navigate to Products page
   - Click "Bulk Upload CSV"
   - Download template
   - Upload template (should create 3 sample products)
   - Verify products appear in table

2. **Test Boxes Upload**:
   - Navigate to Boxes page
   - Click "Bulk Upload CSV"
   - Download template
   - Upload template (should create 3 sample boxes)
   - Verify boxes appear in table

3. **Test Manual Entry**:
   - Click "Add Product" or "Add Box"
   - Fill in form
   - Submit
   - Verify item appears in table

---

## Technical Details

### API Endpoints

**Products CSV Upload**:
```
POST /products/bulk-upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Boxes CSV Upload**:
```
POST /boxes/bulk-upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

### Response Format

```json
{
  "success": true,
  "created_count": 5,
  "errors": null,
  "message": "Successfully created 5 products"
}
```

Or with errors:

```json
{
  "success": true,
  "created_count": 3,
  "errors": [
    {"row": 2, "error": "Invalid SKU format"},
    {"row": 4, "error": "Duplicate SKU"}
  ],
  "message": "Created 3 products with 2 errors"
}
```

---

## Files Modified

### Frontend Changes
- `frontend/src/pages/BoxesPage.tsx` - Fixed field names to match backend
  - Changed `cost` → `cost_per_unit`
  - Removed `max_weight_kg` field
  - Added `usage_count` field
  - Updated form validation
  - Updated table columns

### Backend (Already Working)
- `backend/app/api/products.py` - CSV upload endpoint
- `backend/app/api/boxes.py` - CSV upload endpoint
- Row-by-row validation
- Error reporting
- Transaction handling

---

## Deployment Status

✅ **Frontend**: Running on http://localhost:8080
✅ **Backend**: Running on http://localhost:8000
✅ **Database**: PostgreSQL running correctly
✅ **All Tests**: Passing (100%)

---

## Support

### Check Application Health

```bash
# Backend health check
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### View Logs

```bash
# Backend logs
docker logs packoptima-backend

# Frontend logs
docker logs packoptima-frontend

# Database logs
docker logs packoptima-db
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

---

## Summary

✅ CSV bulk upload working for Products
✅ CSV bulk upload working for Boxes
✅ Manual entry forms still available
✅ Template download working
✅ Error handling and validation working
✅ All tests passing
✅ Professional UI with clear instructions
✅ Application deployed and accessible

**The CSV upload feature is complete and ready for production use!**
