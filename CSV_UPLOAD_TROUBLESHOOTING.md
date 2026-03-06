# CSV Upload Troubleshooting Guide

## Issue: "0 boxes created with 99 errors"

This error typically occurs when the CSV file format doesn't match what the backend expects.

---

## ✅ CORRECT CSV FORMAT

### For Boxes

```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
Medium Box,35,25,15,2.50
Large Box,50,40,20,3.50
```

**CRITICAL REQUIREMENTS**:
1. **Header row MUST be exactly**: `name,length_cm,width_cm,height_cm,cost_per_unit`
2. **No spaces** in column names
3. **No extra columns**
4. **All values required** - no empty cells
5. **Numbers only** for dimensions and cost (no units like "cm" or "$")
6. **Use decimal point** (not comma) for decimals: `1.50` not `1,50`

### For Products

```csv
name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Laptop,LAP-001,Electronics,35,25,5,2.5,150
Mouse,MOU-001,Electronics,12,8,4,0.15,200
```

**CRITICAL REQUIREMENTS**:
1. **Header row MUST be exactly**: `name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume`
2. **SKU must be unique** per company
3. **All fields required**
4. **monthly_order_volume** must be an integer >= 0

---

## ❌ COMMON MISTAKES

### 1. Wrong Column Names

**WRONG**:
```csv
Box Name,Length,Width,Height,Cost
Small Box,20,15,10,1.50
```

**RIGHT**:
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
```

### 2. Extra Columns

**WRONG**:
```csv
name,length_cm,width_cm,height_cm,cost_per_unit,max_weight_kg
Small Box,20,15,10,1.50,5.0
```

**RIGHT** (remove max_weight_kg):
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
```

### 3. Units in Values

**WRONG**:
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20cm,15cm,10cm,$1.50
```

**RIGHT** (numbers only):
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
```

### 4. Empty Cells

**WRONG**:
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,,10,1.50
```

**RIGHT** (all cells filled):
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
```

### 5. Comma as Decimal Separator

**WRONG** (European format):
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1,50
```

**RIGHT** (use period):
```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
```

---

## 🔧 HOW TO FIX

### Step 1: Download the Template

1. Go to Boxes page
2. Click "Bulk Upload CSV"
3. Click "Download CSV Template"
4. Use this template as your starting point

### Step 2: Verify Your CSV File

Open your CSV in a text editor (Notepad, VS Code) and check:

1. **First line** (header) is exactly:
   ```
   name,length_cm,width_cm,height_cm,cost_per_unit
   ```

2. **No extra spaces** before or after commas

3. **All rows have 5 values** (name + 4 numbers)

4. **Numbers use periods** for decimals (1.50 not 1,50)

### Step 3: Test with Simple File

Create a test file with just 2 boxes:

```csv
name,length_cm,width_cm,height_cm,cost_per_unit
Test Box 1,20,15,10,1.50
Test Box 2,30,20,15,2.00
```

Save as `test_boxes.csv` and try uploading.

### Step 4: Check Browser Console

1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Try uploading CSV
4. Look for error messages

### Step 5: Clear Browser Cache

1. Press Ctrl+Shift+Delete
2. Clear cached images and files
3. Reload the page (Ctrl+F5)
4. Try uploading again

---

## 🐛 DEBUG MODE

### Check Backend Logs

```bash
# View recent logs
docker logs packoptima-backend --tail 50

# Follow logs in real-time
docker logs -f packoptima-backend
```

Look for lines like:
```
CSV Headers detected: ['name', 'length_cm', 'width_cm', 'height_cm', 'cost_per_unit']
First row data: {'name': 'Small Box', 'length_cm': '20', ...}
Upload complete: 3 created, 0 errors
```

### Test with API Directly

Use the test script:

```bash
python test_csv_debug.py
```

This will show exactly what's happening with the upload.

---

## 📝 EXAMPLE: Creating CSV in Excel

1. **Open Excel**
2. **Create headers** in row 1:
   - A1: `name`
   - B1: `length_cm`
   - C1: `width_cm`
   - D1: `height_cm`
   - E1: `cost_per_unit`

3. **Add data** in rows 2+:
   - A2: `Small Box`
   - B2: `20`
   - C2: `15`
   - D2: `10`
   - E2: `1.50`

4. **Save As**:
   - File Type: **CSV (Comma delimited) (*.csv)**
   - NOT "CSV UTF-8" or "CSV (Macintosh)"

5. **Verify** by opening in Notepad:
   ```
   name,length_cm,width_cm,height_cm,cost_per_unit
   Small Box,20,15,10,1.5
   ```

---

## 🎯 QUICK FIX CHECKLIST

- [ ] Header row matches exactly: `name,length_cm,width_cm,height_cm,cost_per_unit`
- [ ] No spaces in column names
- [ ] No extra columns (like max_weight_kg)
- [ ] All cells have values (no empty cells)
- [ ] Numbers only (no "cm", "$", or other units)
- [ ] Decimal point (not comma) for decimals
- [ ] File saved as .csv (not .xlsx)
- [ ] File encoding is UTF-8
- [ ] Browser cache cleared
- [ ] Backend container restarted

---

## 🆘 STILL NOT WORKING?

### Option 1: Use Manual Entry

If CSV upload continues to fail, you can add boxes manually:
1. Click "Add Box" button
2. Fill in the form
3. Click "Create"

### Option 2: Check Specific Error

Run the debug script to see exact errors:

```bash
python test_csv_debug.py
```

This will show:
- What headers were detected
- What data was in the first row
- Specific error messages for each row

### Option 3: Restart Everything

```bash
# Stop all containers
docker-compose down

# Start fresh
docker-compose up -d

# Wait 10 seconds for startup
# Then try uploading again
```

---

## ✅ VERIFICATION

After fixing, you should see:

**Success Message**:
```
Successfully uploaded 3 boxes
```

**In the table**:
- All your boxes should appear
- With correct dimensions
- With correct costs

**In backend logs**:
```
CSV Headers detected: ['name', 'length_cm', 'width_cm', 'height_cm', 'cost_per_unit']
Upload complete: 3 created, 0 errors
```

---

## 📞 SUPPORT

If you're still experiencing issues:

1. **Check the exact error message** in the browser
2. **Run the debug script**: `python test_csv_debug.py`
3. **Check backend logs**: `docker logs packoptima-backend --tail 50`
4. **Verify CSV format** matches the template exactly

The most common issue is incorrect column names or extra columns that don't exist in the database schema.
