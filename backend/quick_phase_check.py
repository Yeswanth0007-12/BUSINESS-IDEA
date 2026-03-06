"""Quick phase validation check"""
import os

def check_phase_files():
    """Check if all critical phase files exist"""
    
    files_to_check = {
        'Phase 1': [
            'alembic/versions/004_enhanced_data_models.py',
            'app/models/product.py',
            'app/models/box.py',
        ],
        'Phase 2': [
            'alembic/versions/005_phase2_orientation_fields.py',
            'app/services/optimization_engine.py',
        ],
        'Phase 3': [
            'alembic/versions/006_phase3_shipping_cost_fields.py',
        ],
        'Phase 4': [
            'alembic/versions/007_multi_product_orders.py',
            'app/models/order.py',
            'app/services/order_service.py',
            'app/api/orders.py',
        ],
        'Phase 5': [
            'alembic/versions/008_optimization_tasks.py',
            'app/core/celery_app.py',
            'app/models/optimization_task.py',
            'app/tasks/optimization_tasks.py',
            'app/api/tasks.py',
        ],
        'Phase 6': [
            'alembic/versions/009_bulk_uploads.py',
            'app/models/bulk_upload.py',
            'app/services/bulk_upload_service.py',
            'app/api/bulk_upload.py',
        ],
        'Phase 7': [
            'alembic/versions/010_analytics_tables.py',
            'app/models/analytics_snapshot.py',
            'app/services/analytics_service_v2.py',
        ],
        'Phase 8': [
            'app/api/analytics.py',
        ],
        'Phase 9': [
            'alembic/versions/011_warehouse_integration.py',
            'app/models/api_key.py',
            'app/models/webhook.py',
            'app/schemas/warehouse.py',
            'app/services/warehouse_service.py',
            'app/api/warehouse.py',
            'app/middleware/warehouse_rate_limit.py',
        ],
        'Phase 10': [
            'tests/conftest.py',
            'tests/test_packing_algorithms.py',
            'tests/test_shipping_costs.py',
            'tests/test_multi_product_packing.py',
            'tests/test_bulk_upload.py',
            'tests/test_analytics.py',
            'tests/test_security.py',
            'tests/test_integration_workflows.py',
            'tests/test_performance_benchmarks.py',
            'load_tests/locustfile.py',
            'smoke_tests/test_smoke.py',
        ],
        'Phase 11': [
            '../docs/WAREHOUSE_INTEGRATION_GUIDE.md',
            '../docs/DEPLOYMENT_GUIDE.md',
            '../docs/MONITORING_SETUP_GUIDE.md',
            '../docs/ROLLBACK_PROCEDURES.md',
            '../scripts/deploy_migrations.sh',
            '../scripts/deploy_api.sh',
            '../scripts/deploy_workers.sh',
            '.env.example',
            '.env.production.example',
        ],
    }
    
    print("="*70)
    print("PHASE VALIDATION CHECK")
    print("="*70)
    
    all_complete = True
    
    for phase, files in files_to_check.items():
        print(f"\n{phase}:")
        phase_complete = True
        missing_files = []
        
        for filepath in files:
            if os.path.exists(filepath):
                print(f"  ✓ {filepath}")
            else:
                print(f"  ✗ {filepath} MISSING")
                phase_complete = False
                missing_files.append(filepath)
                all_complete = False
        
        if phase_complete:
            print(f"  → {phase} COMPLETE")
        else:
            print(f"  → {phase} INCOMPLETE ({len(missing_files)} files missing)")
    
    print("\n" + "="*70)
    if all_complete:
        print("✓ ALL PHASES COMPLETE - All required files exist")
    else:
        print("✗ SOME FILES MISSING - Review output above")
    print("="*70)
    
    return all_complete

if __name__ == "__main__":
    check_phase_files()
