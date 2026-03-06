"""
Test script for Phase 6: Bulk Order Processing

This script verifies that all Phase 6 components are properly implemented.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Phase 6 modules can be imported."""
    print("Testing Phase 6 imports...")
    
    try:
        # Test model imports
        from app.models.bulk_upload import BulkUpload, BulkUploadOrder
        print("✓ Bulk upload models imported successfully")
        
        # Test schema imports
        from app.schemas.bulk_upload import (
            BulkUploadResponse,
            BulkUploadSummary,
            BulkUploadOrderResponse,
            BulkUploadFailedOrdersResponse
        )
        print("✓ Bulk upload schemas imported successfully")
        
        # Test service imports
        from app.services.bulk_upload_service import BulkUploadService
        print("✓ Bulk upload service imported successfully")
        
        # Test API imports
        from app.api.bulk_upload import router
        print("✓ Bulk upload API router imported successfully")
        
        # Test task imports
        from app.tasks.optimization_tasks import optimize_order_packing_task
        print("✓ Order packing task imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model_structure():
    """Test that models have correct structure."""
    print("\nTesting model structure...")
    
    try:
        from app.models.bulk_upload import BulkUpload, BulkUploadOrder
        
        # Check BulkUpload attributes
        bulk_upload_attrs = [
            'id', 'company_id', 'filename', 'total_orders',
            'processed_orders', 'failed_orders', 'status',
            'created_at', 'completed_at'
        ]
        
        for attr in bulk_upload_attrs:
            if not hasattr(BulkUpload, attr):
                print(f"✗ BulkUpload missing attribute: {attr}")
                return False
        
        print("✓ BulkUpload model has all required attributes")
        
        # Check BulkUploadOrder attributes
        bulk_order_attrs = [
            'id', 'upload_id', 'row_number', 'order_data',
            'status', 'task_id', 'error_message'
        ]
        
        for attr in bulk_order_attrs:
            if not hasattr(BulkUploadOrder, attr):
                print(f"✗ BulkUploadOrder missing attribute: {attr}")
                return False
        
        print("✓ BulkUploadOrder model has all required attributes")
        
        return True
        
    except Exception as e:
        print(f"✗ Model structure test failed: {str(e)}")
        return False


def test_service_methods():
    """Test that service has required methods."""
    print("\nTesting service methods...")
    
    try:
        from app.services.bulk_upload_service import BulkUploadService
        
        required_methods = [
            'parse_bulk_upload_csv',
            'group_by_order_number',
            'validate_order_data',
            'create_order_from_data',
            'process_bulk_upload',
            'get_bulk_upload_status',
            'get_failed_orders'
        ]
        
        for method in required_methods:
            if not hasattr(BulkUploadService, method):
                print(f"✗ BulkUploadService missing method: {method}")
                return False
        
        print("✓ BulkUploadService has all required methods")
        
        # Check constants
        if not hasattr(BulkUploadService, 'MAX_FILE_SIZE'):
            print("✗ BulkUploadService missing MAX_FILE_SIZE constant")
            return False
        
        if not hasattr(BulkUploadService, 'MAX_ROWS'):
            print("✗ BulkUploadService missing MAX_ROWS constant")
            return False
        
        if not hasattr(BulkUploadService, 'REQUIRED_HEADERS'):
            print("✗ BulkUploadService missing REQUIRED_HEADERS constant")
            return False
        
        print("✓ BulkUploadService has all required constants")
        
        # Verify constants values
        if BulkUploadService.MAX_FILE_SIZE != 10 * 1024 * 1024:
            print(f"✗ MAX_FILE_SIZE should be 10 MB, got {BulkUploadService.MAX_FILE_SIZE}")
            return False
        
        if BulkUploadService.MAX_ROWS != 10000:
            print(f"✗ MAX_ROWS should be 10000, got {BulkUploadService.MAX_ROWS}")
            return False
        
        expected_headers = ["order_number", "customer_name", "product_sku", "quantity"]
        if BulkUploadService.REQUIRED_HEADERS != expected_headers:
            print(f"✗ REQUIRED_HEADERS mismatch")
            return False
        
        print("✓ BulkUploadService constants have correct values")
        
        return True
        
    except Exception as e:
        print(f"✗ Service methods test failed: {str(e)}")
        return False


def test_api_endpoints():
    """Test that API router has required endpoints."""
    print("\nTesting API endpoints...")
    
    try:
        from app.api.bulk_upload import router
        
        # Check router configuration
        if router.prefix != "/api/v1/bulk-upload":
            print(f"✗ Router prefix should be '/api/v1/bulk-upload', got '{router.prefix}'")
            return False
        
        print("✓ Router has correct prefix")
        
        # Check routes exist
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            "",  # POST for upload
            "/{upload_id}",  # GET for status
            "/{upload_id}/failed"  # GET for failed orders
        ]
        
        for expected_route in expected_routes:
            if expected_route not in routes:
                print(f"✗ Missing route: {expected_route}")
                return False
        
        print("✓ Router has all required endpoints")
        
        return True
        
    except Exception as e:
        print(f"✗ API endpoints test failed: {str(e)}")
        return False


def test_migration_file():
    """Test that migration file exists and has correct structure."""
    print("\nTesting migration file...")
    
    migration_path = "alembic/versions/009_bulk_uploads.py"
    
    if not os.path.exists(migration_path):
        print(f"✗ Migration file not found: {migration_path}")
        return False
    
    print("✓ Migration file exists")
    
    # Read migration file
    with open(migration_path, 'r') as f:
        content = f.read()
    
    # Check for required elements
    required_elements = [
        "revision = '009_bulk_uploads'",
        "down_revision = '008_optimization_tasks'",
        "def upgrade():",
        "def downgrade():",
        "bulk_uploads",
        "bulk_upload_orders"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"✗ Migration missing element: {element}")
            return False
    
    print("✓ Migration file has correct structure")
    
    return True


def test_main_app_registration():
    """Test that bulk upload router is registered in main app."""
    print("\nTesting main app registration...")
    
    try:
        # Read main.py
        with open("app/main.py", 'r') as f:
            content = f.read()
        
        # Check import
        if "bulk_upload" not in content:
            print("✗ bulk_upload not imported in main.py")
            return False
        
        print("✓ bulk_upload imported in main.py")
        
        # Check router registration
        if "app.include_router(bulk_upload.router)" not in content:
            print("✗ bulk_upload.router not registered in main.py")
            return False
        
        print("✓ bulk_upload.router registered in main.py")
        
        return True
        
    except Exception as e:
        print(f"✗ Main app registration test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 6: Bulk Order Processing - Implementation Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Model Structure", test_model_structure),
        ("Service Methods", test_service_methods),
        ("API Endpoints", test_api_endpoints),
        ("Migration File", test_migration_file),
        ("Main App Registration", test_main_app_registration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 6 implementation tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
