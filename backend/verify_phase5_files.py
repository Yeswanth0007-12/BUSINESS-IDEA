"""
Simple file verification for Phase 5: Queue System Architecture
Checks that all required files exist and have basic structure.
"""
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists."""
    if path.exists():
        print(f"✓ {description}: {path.name}")
        return True
    else:
        print(f"❌ {description} missing: {path}")
        return False

def check_file_contains(path, keywords, description):
    """Check if file contains required keywords."""
    if not path.exists():
        print(f"❌ {description}: File not found")
        return False
    
    content = path.read_text()
    missing = []
    for keyword in keywords:
        if keyword not in content:
            missing.append(keyword)
    
    if missing:
        print(f"❌ {description}: Missing keywords: {', '.join(missing)}")
        return False
    else:
        print(f"✓ {description}: All keywords present")
        return True

def main():
    """Verify Phase 5 files."""
    print("=" * 60)
    print("Phase 5: Queue System Architecture - File Verification")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    results = []
    
    # Check requirements.txt
    print("\n1. Dependencies:")
    req_file = backend_dir / "requirements.txt"
    results.append(check_file_contains(
        req_file,
        ["redis==5.0.1", "celery==5.3.4", "flower==2.0.1"],
        "requirements.txt has Redis/Celery"
    ))
    
    # Check .env
    print("\n2. Environment Configuration:")
    env_file = backend_dir / ".env"
    results.append(check_file_contains(
        env_file,
        ["REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"],
        ".env has Redis config"
    ))
    
    # Check config.py
    print("\n3. Config Settings:")
    config_file = backend_dir / "app" / "core" / "config.py"
    results.append(check_file_contains(
        config_file,
        ["REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"],
        "config.py has Redis settings"
    ))
    
    # Check Celery app
    print("\n4. Celery Application:")
    celery_file = backend_dir / "app" / "core" / "celery_app.py"
    results.append(check_file_exists(celery_file, "celery_app.py"))
    results.append(check_file_contains(
        celery_file,
        ["from celery import Celery", "celery_app = Celery", "task_serializer"],
        "celery_app.py structure"
    ))
    
    # Check OptimizationTask model
    print("\n5. OptimizationTask Model:")
    model_file = backend_dir / "app" / "models" / "optimization_task.py"
    results.append(check_file_exists(model_file, "optimization_task.py"))
    results.append(check_file_contains(
        model_file,
        ["class OptimizationTask", "UUID", "status", "progress", "result_id"],
        "OptimizationTask model structure"
    ))
    
    # Check migration
    print("\n6. Database Migration:")
    migration_file = backend_dir / "alembic" / "versions" / "008_optimization_tasks.py"
    results.append(check_file_exists(migration_file, "008_optimization_tasks.py"))
    results.append(check_file_contains(
        migration_file,
        ["revision = '008_optimization_tasks'", "create_table", "optimization_tasks"],
        "Migration structure"
    ))
    
    # Check task schemas
    print("\n7. Task Schemas:")
    schema_file = backend_dir / "app" / "schemas" / "task.py"
    results.append(check_file_exists(schema_file, "task.py"))
    results.append(check_file_contains(
        schema_file,
        ["TaskSubmitResponse", "TaskStatusResponse", "TaskResultResponse"],
        "Task schemas"
    ))
    
    # Check Celery tasks
    print("\n8. Celery Tasks:")
    tasks_file = backend_dir / "app" / "tasks" / "optimization_tasks.py"
    results.append(check_file_exists(tasks_file, "optimization_tasks.py"))
    results.append(check_file_contains(
        tasks_file,
        ["optimize_packaging_task", "optimize_order_task", "@celery_app.task"],
        "Celery task functions"
    ))
    
    # Check API endpoints
    print("\n9. API Endpoints:")
    tasks_api = backend_dir / "app" / "api" / "tasks.py"
    results.append(check_file_exists(tasks_api, "tasks.py API"))
    results.append(check_file_contains(
        tasks_api,
        ["get_task_status", "get_task_result", "@router.get"],
        "Task API endpoints"
    ))
    
    opt_api = backend_dir / "app" / "api" / "optimization.py"
    results.append(check_file_contains(
        opt_api,
        ["run_optimization_async", "/async", "TaskSubmitResponse"],
        "Async optimization endpoint"
    ))
    
    # Check main.py registration
    print("\n10. Router Registration:")
    main_file = backend_dir / "app" / "main.py"
    results.append(check_file_contains(
        main_file,
        ["from app.api import", "tasks", "app.include_router(tasks.router)"],
        "Tasks router registered"
    ))
    
    # Check worker script
    print("\n11. Worker Startup Script:")
    worker_script = backend_dir / "start_worker.sh"
    results.append(check_file_exists(worker_script, "start_worker.sh"))
    results.append(check_file_contains(
        worker_script,
        ["celery -A app.core.celery_app worker", "--loglevel=info"],
        "Worker script content"
    ))
    
    # Check docker-compose
    print("\n12. Docker Compose:")
    docker_file = backend_dir.parent / "docker-compose.yml"
    results.append(check_file_contains(
        docker_file,
        ["redis:", "celery-worker:", "REDIS_URL", "CELERY_BROKER_URL"],
        "Docker Compose has Redis and Celery"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All Phase 5 files are in place and properly structured!")
        print("\nNext steps to test the queue system:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Redis: docker run -d -p 6379:6379 redis:7-alpine")
        print("3. Run migrations: alembic upgrade head")
        print("4. Start Celery worker: ./start_worker.sh (or use docker-compose)")
        print("5. Test async endpoints via API")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
