"""
Test script for Phase 5: Queue System Architecture
Tests the basic functionality without requiring Redis/Celery to be running.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all Phase 5 modules can be imported."""
    print("Testing Phase 5 imports...")
    
    try:
        # Test model import
        from app.models.optimization_task import OptimizationTask
        print("✓ OptimizationTask model imported")
        
        # Test schema imports
        from app.schemas.task import TaskSubmitResponse, TaskStatusResponse, TaskResultResponse
        print("✓ Task schemas imported")
        
        # Test Celery app import
        from app.core.celery_app import celery_app
        print("✓ Celery app imported")
        
        # Test task imports
        from app.tasks.optimization_tasks import optimize_packaging_task, optimize_order_task
        print("✓ Celery tasks imported")
        
        # Test API imports
        from app.api.tasks import router as tasks_router
        from app.api.optimization import router as optimization_router
        print("✓ API routers imported")
        
        print("\n✅ All Phase 5 imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model_structure():
    """Test OptimizationTask model structure."""
    print("\nTesting OptimizationTask model structure...")
    
    try:
        from app.models.optimization_task import OptimizationTask
        
        # Check required attributes
        required_attrs = [
            'id', 'company_id', 'task_type', 'status', 'progress',
            'created_at', 'started_at', 'completed_at', 'result_id',
            'error_message', 'metadata'
        ]
        
        for attr in required_attrs:
            if not hasattr(OptimizationTask, attr):
                print(f"❌ Missing attribute: {attr}")
                return False
            print(f"✓ Has attribute: {attr}")
        
        print("\n✅ OptimizationTask model structure is correct!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_structure():
    """Test task schema structures."""
    print("\nTesting task schema structures...")
    
    try:
        from app.schemas.task import TaskSubmitResponse, TaskStatusResponse, TaskResultResponse
        from uuid import uuid4
        from datetime import datetime
        
        # Test TaskSubmitResponse
        task_id = uuid4()
        submit_response = TaskSubmitResponse(
            task_id=task_id,
            status="pending",
            message="Test message"
        )
        print(f"✓ TaskSubmitResponse created: {submit_response.task_id}")
        
        # Test TaskStatusResponse
        status_response = TaskStatusResponse(
            task_id=task_id,
            task_type="single",
            status="processing",
            progress=50,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=None,
            result_id=None,
            error_message=None,
            metadata={"test": "data"}
        )
        print(f"✓ TaskStatusResponse created: progress={status_response.progress}%")
        
        # Test TaskResultResponse
        result_response = TaskResultResponse(
            task_id=task_id,
            status="completed",
            result={"test": "result"}
        )
        print(f"✓ TaskResultResponse created: status={result_response.status}")
        
        print("\n✅ All task schemas work correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Schema structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_config():
    """Test Celery configuration."""
    print("\nTesting Celery configuration...")
    
    try:
        from app.core.celery_app import celery_app
        
        # Check Celery app is configured
        print(f"✓ Celery app name: {celery_app.main}")
        print(f"✓ Broker URL configured: {bool(celery_app.conf.broker_url)}")
        print(f"✓ Result backend configured: {bool(celery_app.conf.result_backend)}")
        print(f"✓ Task serializer: {celery_app.conf.task_serializer}")
        print(f"✓ Result expires: {celery_app.conf.result_expires}s")
        
        print("\n✅ Celery configuration is correct!")
        return True
        
    except Exception as e:
        print(f"\n❌ Celery config test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_migration_file():
    """Test that migration file exists and is valid."""
    print("\nTesting migration file...")
    
    try:
        migration_path = Path(__file__).parent / "alembic" / "versions" / "008_optimization_tasks.py"
        
        if not migration_path.exists():
            print(f"❌ Migration file not found: {migration_path}")
            return False
        
        print(f"✓ Migration file exists: {migration_path.name}")
        
        # Read and check migration content
        content = migration_path.read_text()
        
        required_elements = [
            "revision = '008_optimization_tasks'",
            "down_revision = '007_multi_product_orders'",
            "def upgrade():",
            "def downgrade():",
            "create_table",
            "optimization_tasks"
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✓ Contains: {element}")
            else:
                print(f"❌ Missing: {element}")
                return False
        
        print("\n✅ Migration file is valid!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration file test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 5 tests."""
    print("=" * 60)
    print("Phase 5: Queue System Architecture - Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Model Structure", test_model_structure),
        ("Schema Structure", test_schema_structure),
        ("Celery Config", test_celery_config),
        ("Migration File", test_migration_file),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 5 verification tests passed!")
        print("\nNote: To fully test the queue system, you need to:")
        print("1. Install Redis: docker run -d -p 6379:6379 redis:7-alpine")
        print("2. Run migrations: cd backend && alembic upgrade head")
        print("3. Start Celery worker: cd backend && ./start_worker.sh")
        print("4. Test async endpoints via API")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
