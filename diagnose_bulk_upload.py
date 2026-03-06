"""
Diagnostic script for bulk order CSV uploads.

This script helps identify why your CSV upload is failing.
"""
import csv
import sys
import requests
from typing import List, Set

def check_csv_format(filepath: str) -> tuple[bool, List[str]]:
    """Check if CSV has correct format."""
    errors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check headers
            required_headers = ["order_number", "customer_name", "product_sku", "quantity"]
            if not reader.fieldnames:
                errors.append("❌ CSV file is empty")
                return False, errors
            
            missing_headers = set(required_headers) - set(reader.fieldnames)
            if missing_headers:
                errors.append(f"❌ Missing required columns: {', '.join(missing_headers)}")
                errors.append(f"   Found columns: {', '.join(reader.fieldnames)}")
                errors.append(f"   Required columns: {', '.join(required_headers)}")
                return False, errors
            
            print("✅ CSV headers are correct")
            
            # Check rows
            rows = list(reader)
            if not rows:
                errors.append("❌ CSV has no data rows")
                return False, errors
            
            print(f"✅ CSV has {len(rows)} data rows")
            
            # Validate each row
            skus = set()
            order_numbers = set()
            row_errors = []
            
            for i, row in enumerate(rows, start=2):  # Start at 2 (header is row 1)
                # Check for empty values
                for header in required_headers:
                    if not row.get(header, "").strip():
                        row_errors.append(f"   Row {i}: Missing value for '{header}'")
                
                # Check quantity is valid
                try:
                    qty = int(row["quantity"])
                    if qty <= 0:
                        row_errors.append(f"   Row {i}: Quantity must be positive (got {qty})")
                except ValueError:
                    row_errors.append(f"   Row {i}: Invalid quantity '{row['quantity']}' - must be an integer")
                
                # Collect SKUs and order numbers
                if row.get("product_sku"):
                    skus.add(row["product_sku"].strip())
                if row.get("order_number"):
                    order_numbers.add(row["order_number"].strip())
            
            if row_errors:
                errors.append("❌ Row validation errors:")
                errors.extend(row_errors[:10])  # Show first 10 errors
                if len(row_errors) > 10:
                    errors.append(f"   ... and {len(row_errors) - 10} more errors")
                return False, errors
            
            print(f"✅ All rows are valid")
            print(f"   Found {len(order_numbers)} unique orders")
            print(f"   Found {len(skus)} unique SKUs: {', '.join(sorted(skus))}")
            
            return True, []
            
    except FileNotFoundError:
        errors.append(f"❌ File not found: {filepath}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Error reading CSV: {str(e)}")
        return False, errors

def check_products_exist(skus: Set[str], token: str, base_url: str = "http://localhost:8000") -> tuple[bool, List[str]]:
    """Check if product SKUs exist in the database."""
    errors = []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/products", headers=headers, params={"limit": 10000})
        
        if response.status_code != 200:
            errors.append(f"❌ Failed to fetch products: {response.status_code}")
            return False, errors
        
        products = response.json()
        existing_skus = {p["sku"] for p in products}
        
        print(f"✅ Found {len(existing_skus)} products in database")
        
        missing_skus = skus - existing_skus
        
        if missing_skus:
            errors.append(f"❌ These SKUs don't exist in your Products database:")
            for sku in sorted(missing_skus):
                errors.append(f"   - {sku}")
            errors.append("")
            errors.append("   To fix this:")
            errors.append("   1. Go to Products tab and create these products")
            errors.append("   2. OR update your CSV to use existing SKUs")
            return False, errors
        
        print(f"✅ All SKUs exist in database")
        return True, []
        
    except Exception as e:
        errors.append(f"⚠️  Could not verify SKUs in database: {str(e)}")
        errors.append("   Make sure the backend is running and you're logged in")
        return False, errors

def main():
    print("=" * 80)
    print("BULK ORDER CSV DIAGNOSTIC TOOL")
    print("=" * 80)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python diagnose_bulk_upload.py <csv_file> [auth_token]")
        print()
        print("Example:")
        print("  python diagnose_bulk_upload.py my_orders.csv")
        print("  python diagnose_bulk_upload.py my_orders.csv eyJhbGc...")
        print()
        sys.exit(1)
    
    filepath = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Checking CSV file: {filepath}")
    print()
    
    # Step 1: Check CSV format
    print("Step 1: Checking CSV format...")
    print("-" * 80)
    is_valid, errors = check_csv_format(filepath)
    
    if not is_valid:
        print()
        for error in errors:
            print(error)
        print()
        print("=" * 80)
        print("❌ CSV FORMAT IS INVALID")
        print("=" * 80)
        print()
        print("Please fix the errors above and try again.")
        print("See BULK_ORDER_CSV_FORMAT_GUIDE.md for detailed format requirements.")
        sys.exit(1)
    
    # Extract SKUs for Step 2
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        skus = {row["product_sku"].strip() for row in reader if row.get("product_sku")}
    
    print()
    
    # Step 2: Check if products exist (optional, requires auth token)
    if token:
        print("Step 2: Checking if product SKUs exist in database...")
        print("-" * 80)
        is_valid, errors = check_products_exist(skus, token)
        
        if not is_valid:
            print()
            for error in errors:
                print(error)
            print()
            print("=" * 80)
            print("❌ PRODUCT SKUs NOT FOUND")
            print("=" * 80)
            sys.exit(1)
    else:
        print("Step 2: Skipping product SKU verification (no auth token provided)")
        print("-" * 80)
        print("⚠️  To verify SKUs exist in database, provide your auth token:")
        print(f"   python diagnose_bulk_upload.py {filepath} YOUR_AUTH_TOKEN")
        print()
        print(f"   SKUs in your CSV: {', '.join(sorted(skus))}")
        print("   Make sure these exist in your Products tab before uploading.")
    
    print()
    print("=" * 80)
    print("✅ CSV FILE IS VALID")
    print("=" * 80)
    print()
    print("Your CSV file should upload successfully!")
    print()
    print("Next steps:")
    print("1. Go to Bulk Upload tab in PackOptima")
    print("2. Upload your CSV file")
    print("3. Check the results")

if __name__ == "__main__":
    main()
