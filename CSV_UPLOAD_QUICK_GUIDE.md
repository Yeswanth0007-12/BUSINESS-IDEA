# CSV Bulk Upload - Quick Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Click "Bulk Upload CSV"
On Products or Boxes page, click the **green button** labeled "Bulk Upload CSV"

### Step 2: Download Template (Optional)
Click "Download CSV Template" to get a sample file with the correct format

### Step 3: Upload Your File
- Click "Select CSV File"
- Choose your CSV file
- Click "Upload"
- Done!

---

## 📊 CSV Format

### Products CSV
```
name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
Gaming Laptop,LAPTOP-001,Electronics,40,30,5,3.5,100
Smartphone,PHONE-001,Electronics,15,8,1,0.2,500
```

### Boxes CSV
```
name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
Medium Box,35,25,15,2.50
```

---

## 🎯 Where to Find It

### Products Page
```
http://localhost:8080/products

┌──────────────────────────────────────────────────┐
│ Products                                          │
│ Manage your product catalog                      │
│                                                   │
│              [🟢 Bulk Upload CSV] [🔵 Add Product]│
└──────────────────────────────────────────────────┘
```

### Boxes Page
```
http://localhost:8080/boxes

┌──────────────────────────────────────────────────┐
│ Boxes                                             │
│ Manage your box inventory                        │
│                                                   │
│              [🟢 Bulk Upload CSV] [🔵 Add Box]    │
└──────────────────────────────────────────────────┘
```

---

## ✅ Features

- ✅ Upload hundreds of items at once
- ✅ Download template with examples
- ✅ Clear error messages if something goes wrong
- ✅ Automatic table refresh after upload
- ✅ **Manual entry still works** (blue "Add" button)

---

## 💡 Tips

1. **Use Excel or Google Sheets** to prepare your CSV
2. **Download the template first** to see the correct format
3. **Check your data** before uploading (no empty cells)
4. **Save as CSV** format (.csv extension)
5. **Upload and verify** - check the table after upload

---

## 🎊 Benefits

- **Save time**: Upload 100 products in 30 seconds vs 30 minutes manually
- **Less errors**: Prepare data in spreadsheet with validation
- **Professional**: Enterprise-grade bulk import feature
- **Flexible**: Use bulk upload OR manual entry - your choice!

---

**Read the full guide**: `CSV_BULK_UPLOAD_FEATURE.md`
