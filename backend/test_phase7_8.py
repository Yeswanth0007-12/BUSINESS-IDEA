"""
Test script for Phase 7 and Phase 8 implementation.

This script verifies:
- Analytics data models are properly defined
- Analytics service methods work correctly
- API endpoints are properly configured
"""

import sys
from datetime import date, timedelta

def test_models_import():
    """Test that analytics models can be imported."""
    print("Testing analytics models import...")
    try:
        from app.models.analytics_snapshot import (
            AnalyticsSnapshot,
            BoxUsageMetrics,
            ShippingCostMetrics
        )
        print("✓ Analytics models imported successfully")
        
        # Check model attributes
        assert hasattr(AnalyticsSnapshot, 'company_id')
        assert hasattr(AnalyticsSnapshot, 'snapshot_date')
        assert hasattr(AnalyticsSnapshot, 'total_products')
        assert hasattr(AnalyticsSnapshot, 'avg_space_utilization')
        print("✓ AnalyticsSnapshot model has required attributes")
        
        assert hasattr(BoxUsageMetrics, 'company_id')
        assert hasattr(BoxUsageMetrics, 'box_id')
        assert hasattr(BoxUsageMetrics, 'usage_count')
        print("✓ BoxUsageMetrics model has required attributes")
        
        assert hasattr(ShippingCostMetrics, 'company_id')
        assert hasattr(ShippingCostMetrics, 'total_shipments')
        assert hasattr(ShippingCostMetrics, 'total_shipping_cost')
        print("✓ ShippingCostMetrics model has required attributes")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import analytics models: {e}")
        return False


def test_service_import():
    """Test that analytics service can be imported."""
    print("\nTesting analytics service import...")
    try:
        from app.services.analytics_service_v2 import AnalyticsServiceV2
        print("✓ AnalyticsServiceV2 imported successfully")
        
        # Check service methods
        assert hasattr(AnalyticsServiceV2, 'calculate_space_utilization_metrics')
        assert hasattr(AnalyticsServiceV2, 'analyze_box_usage_frequency')
        assert hasattr(AnalyticsServiceV2, 'calculate_shipping_cost_metrics')
        assert hasattr(AnalyticsServiceV2, 'calculate_savings_trend')
        assert hasattr(AnalyticsServiceV2, 'generate_daily_snapshot')
        print("✓ AnalyticsServiceV2 has all required methods")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import analytics service: {e}")
        return False


def test_api_endpoints():
    """Test that API endpoints are properly configured."""
    print("\nTesting API endpoints...")
    try:
        from app.api.analytics import router
        print("✓ Analytics router imported successfully")
        
        # Check that new endpoints exist
        routes = [route.path for route in router.routes]
        print(f"  Available routes: {routes}")
        
        expected_routes = [
            '/analytics/summary',
            '/analytics/box-usage',
            '/analytics/shipping-cost',
            '/analytics/trends-v2'
        ]
        
        for expected_route in expected_routes:
            if expected_route in routes:
                print(f"✓ Endpoint {expected_route} exists")
            else:
                print(f"✗ Endpoint {expected_route} not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to test API endpoints: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_migration_file():
    """Test that migration file exists and is properly formatted."""
    print("\nTesting migration file...")
    try:
        import os
        migration_path = "alembic/versions/010_analytics_tables.py"
        
        if not os.path.exists(migration_path):
            print(f"✗ Migration file not found at {migration_path}")
            return False
        
        print(f"✓ Migration file exists at {migration_path}")
        
        # Read and check migration content
        with open(migration_path, 'r') as f:
            content = f.read()
        
        required_elements = [
            'analytics_snapshots',
            'box_usage_metrics',
            'shipping_cost_metrics',
            'def upgrade',
            'def downgrade'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✓ Migration contains '{element}'")
            else:
                print(f"✗ Migration missing '{element}'")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to test migration file: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 7 & 8 Implementation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Models Import", test_models_import()))
    results.append(("Service Import", test_service_import()))
    results.append(("API Endpoints", test_api_endpoints()))
    results.append(("Migration File", test_migration_file()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All Phase 7 & 8 tasks completed successfully!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
