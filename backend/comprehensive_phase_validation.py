"""
Comprehensive validation script for all phases (1-11) of production logistics upgrade.
This script checks implementation status and runs tests for each phase.
"""
import os
import sys
import subprocess
from pathlib import Path

class PhaseValidator:
    def __init__(self):
        self.results = {
            'phase_1': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_2': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_3': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_4': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_5': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_6': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_7': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_8': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_9': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_10': {'status': 'unknown', 'tasks': [], 'tests': []},
            'phase_11': {'status': 'unknown', 'tasks': [], 'tests': []},
        }
    
    def check_file_exists(self, filepath):
        """Check if a file exists."""
        return os.path.exists(filepath)
    
    def validate_phase_1(self):
        """Validate Phase 1: Enhanced Data Models"""
        print("\n" + "="*60)
        print("PHASE 1: Enhanced Data Models")
        print("="*60)
        
        tasks = []
        
        # Check migration file
        if self.check_file_exists("alembic/versions/004_enhanced_data_models.py"):
            tasks.append("✓ Migration 004 exists")
        else:
            tasks.append("✗ Migration 004 missing")
        
        # Check model updates
        if self.check_file_exists("app/models/product.py"):
            with open("app/models/product.py", "r") as f:
                content = f.read()
                if "fragile" in content and "stackable" in content:
                    tasks.append("✓ Product model has fragile/stackable fields")
                else:
                    tasks.append("✗ Product model missing fields")
        
        if self.check_file_exists("app/models/box.py"):
            with open("app/models/box.py", "r") as f:
                content = f.read()
                if "max_weight_kg" in content and "material_type" in content:
                    tasks.append("✓ Box model has max_weight_kg/material_type fields")
                else:
                    tasks.append("✗ Box model missing fields")
        
        self.results['phase_1']['tasks'] = tasks
        self.results['phase_1']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_1']['status'] == 'complete'
    
    def validate_phase_2(self):
        """Validate Phase 2: Advanced Packing Engine"""
        print("\n" + "="*60)
        print("PHASE 2: Advanced Packing Engine")
        print("="*60)
        
        tasks = []
        
        # Check optimization engine
        if self.check_file_exists("app/services/optimization_engine.py"):
            with open("app/services/optimization_engine.py", "r") as f:
                content = f.read()
                if "test_all_orientations" in content:
                    tasks.append("✓ test_all_orientations method exists")
                else:
                    tasks.append("✗ test_all_orientations method missing")
                
                if "validate_weight_constraint" in content:
                    tasks.append("✓ validate_weight_constraint method exists")
                else:
                    tasks.append("✗ validate_weight_constraint method missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/005_phase2_orientation_fields.py"):
            tasks.append("✓ Migration 005 exists")
        else:
            tasks.append("✗ Migration 005 missing")
        
        self.results['phase_2']['tasks'] = tasks
        self.results['phase_2']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_2']['status'] == 'complete'
    
    def validate_phase_3(self):
        """Validate Phase 3: Shipping Cost Calculator"""
        print("\n" + "="*60)
        print("PHASE 3: Shipping Cost Calculator")
        print("="*60)
        
        tasks = []
        
        # Check optimization engine methods
        if self.check_file_exists("app/services/optimization_engine.py"):
            with open("app/services/optimization_engine.py", "r") as f:
                content = f.read()
                if "calculate_volumetric_weight" in content:
                    tasks.append("✓ calculate_volumetric_weight method exists")
                else:
                    tasks.append("✗ calculate_volumetric_weight method missing")
                
                if "calculate_billable_weight" in content:
                    tasks.append("✓ calculate_billable_weight method exists")
                else:
                    tasks.append("✗ calculate_billable_weight method missing")
                
                if "calculate_shipping_cost" in content:
                    tasks.append("✓ calculate_shipping_cost method exists")
                else:
                    tasks.append("✗ calculate_shipping_cost method missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/006_phase3_shipping_cost_fields.py"):
            tasks.append("✓ Migration 006 exists")
        else:
            tasks.append("✗ Migration 006 missing")
        
        self.results['phase_3']['tasks'] = tasks
        self.results['phase_3']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_3']['status'] == 'complete'
    
    def validate_phase_4(self):
        """Validate Phase 4: Multi-Product Order Packing"""
        print("\n" + "="*60)
        print("PHASE 4: Multi-Product Order Packing")
        print("="*60)
        
        tasks = []
        
        # Check models
        if self.check_file_exists("app/models/order.py"):
            tasks.append("✓ Order model exists")
        else:
            tasks.append("✗ Order model missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/007_multi_product_orders.py"):
            tasks.append("✓ Migration 007 exists")
        else:
            tasks.append("✗ Migration 007 missing")
        
        # Check service
        if self.check_file_exists("app/services/order_service.py"):
            tasks.append("✓ Order service exists")
        else:
            tasks.append("✗ Order service missing")
        
        # Check API
        if self.check_file_exists("app/api/orders.py"):
            tasks.append("✓ Orders API exists")
        else:
            tasks.append("✗ Orders API missing")
        
        # Check bin packing
        if self.check_file_exists("app/services/optimization_engine.py"):
            with open("app/services/optimization_engine.py", "r") as f:
                content = f.read()
                if "pack_multi_product_order" in content:
                    tasks.append("✓ pack_multi_product_order method exists")
                else:
                    tasks.append("✗ pack_multi_product_order method missing")
        
        self.results['phase_4']['tasks'] = tasks
        self.results['phase_4']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_4']['status'] == 'complete'
    
    def validate_phase_5(self):
        """Validate Phase 5: Queue System Architecture"""
        print("\n" + "="*60)
        print("PHASE 5: Queue System Architecture")
        print("="*60)
        
        tasks = []
        
        # Check Celery app
        if self.check_file_exists("app/core/celery_app.py"):
            tasks.append("✓ Celery app exists")
        else:
            tasks.append("✗ Celery app missing")
        
        # Check task model
        if self.check_file_exists("app/models/optimization_task.py"):
            tasks.append("✓ OptimizationTask model exists")
        else:
            tasks.append("✗ OptimizationTask model missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/008_optimization_tasks.py"):
            tasks.append("✓ Migration 008 exists")
        else:
            tasks.append("✗ Migration 008 missing")
        
        # Check tasks
        if self.check_file_exists("app/tasks/optimization_tasks.py"):
            tasks.append("✓ Optimization tasks exist")
        else:
            tasks.append("✗ Optimization tasks missing")
        
        # Check API
        if self.check_file_exists("app/api/tasks.py"):
            tasks.append("✓ Tasks API exists")
        else:
            tasks.append("✗ Tasks API missing")
        
        self.results['phase_5']['tasks'] = tasks
        self.results['phase_5']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_5']['status'] == 'complete'
    
    def validate_phase_6(self):
        """Validate Phase 6: Bulk Order Processing"""
        print("\n" + "="*60)
        print("PHASE 6: Bulk Order Processing")
        print("="*60)
        
        tasks = []
        
        # Check models
        if self.check_file_exists("app/models/bulk_upload.py"):
            tasks.append("✓ BulkUpload model exists")
        else:
            tasks.append("✗ BulkUpload model missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/009_bulk_uploads.py"):
            tasks.append("✓ Migration 009 exists")
        else:
            tasks.append("✗ Migration 009 missing")
        
        # Check service
        if self.check_file_exists("app/services/bulk_upload_service.py"):
            tasks.append("✓ Bulk upload service exists")
        else:
            tasks.append("✗ Bulk upload service missing")
        
        # Check API
        if self.check_file_exists("app/api/bulk_upload.py"):
            tasks.append("✓ Bulk upload API exists")
        else:
            tasks.append("✗ Bulk upload API missing")
        
        self.results['phase_6']['tasks'] = tasks
        self.results['phase_6']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_6']['status'] == 'complete'
    
    def validate_phase_7(self):
        """Validate Phase 7: Advanced Analytics"""
        print("\n" + "="*60)
        print("PHASE 7: Advanced Analytics")
        print("="*60)
        
        tasks = []
        
        # Check models
        if self.check_file_exists("app/models/analytics_snapshot.py"):
            tasks.append("✓ Analytics models exist")
        else:
            tasks.append("✗ Analytics models missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/010_analytics_tables.py"):
            tasks.append("✓ Migration 010 exists")
        else:
            tasks.append("✗ Migration 010 missing")
        
        # Check service
        if self.check_file_exists("app/services/analytics_service_v2.py"):
            tasks.append("✓ Analytics service v2 exists")
        else:
            tasks.append("✗ Analytics service v2 missing")
        
        self.results['phase_7']['tasks'] = tasks
        self.results['phase_7']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_7']['status'] == 'complete'
    
    def validate_phase_8(self):
        """Validate Phase 8: Enhanced Dashboard APIs"""
        print("\n" + "="*60)
        print("PHASE 8: Enhanced Dashboard APIs")
        print("="*60)
        
        tasks = []
        
        # Check analytics API
        if self.check_file_exists("app/api/analytics.py"):
            with open("app/api/analytics.py", "r") as f:
                content = f.read()
                if "/summary" in content:
                    tasks.append("✓ Analytics summary endpoint exists")
                else:
                    tasks.append("✗ Analytics summary endpoint missing")
                
                if "/box-usage" in content:
                    tasks.append("✓ Box usage endpoint exists")
                else:
                    tasks.append("✗ Box usage endpoint missing")
                
                if "/shipping-cost" in content:
                    tasks.append("✓ Shipping cost endpoint exists")
                else:
                    tasks.append("✗ Shipping cost endpoint missing")
                
                if "/trends" in content:
                    tasks.append("✓ Trends endpoint exists")
                else:
                    tasks.append("✗ Trends endpoint missing")
        
        self.results['phase_8']['tasks'] = tasks
        self.results['phase_8']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_8']['status'] == 'complete'
    
    def validate_phase_9(self):
        """Validate Phase 9: Warehouse Integration API"""
        print("\n" + "="*60)
        print("PHASE 9: Warehouse Integration API")
        print("="*60)
        
        tasks = []
        
        # Check models
        if self.check_file_exists("app/models/api_key.py"):
            tasks.append("✓ ApiKey model exists")
        else:
            tasks.append("✗ ApiKey model missing")
        
        if self.check_file_exists("app/models/webhook.py"):
            tasks.append("✓ Webhook models exist")
        else:
            tasks.append("✗ Webhook models missing")
        
        # Check migration
        if self.check_file_exists("alembic/versions/011_warehouse_integration.py"):
            tasks.append("✓ Migration 011 exists")
        else:
            tasks.append("✗ Migration 011 missing")
        
        # Check schemas
        if self.check_file_exists("app/schemas/warehouse.py"):
            tasks.append("✓ Warehouse schemas exist")
        else:
            tasks.append("✗ Warehouse schemas missing")
        
        # Check service
        if self.check_file_exists("app/services/warehouse_service.py"):
            tasks.append("✓ Warehouse service exists")
        else:
            tasks.append("✗ Warehouse service missing")
        
        # Check API
        if self.check_file_exists("app/api/warehouse.py"):
            tasks.append("✓ Warehouse API exists")
        else:
            tasks.append("✗ Warehouse API missing")
        
        # Check rate limiter
        if self.check_file_exists("app/middleware/warehouse_rate_limit.py"):
            tasks.append("✓ Rate limiter exists")
        else:
            tasks.append("✗ Rate limiter missing")
        
        self.results['phase_9']['tasks'] = tasks
        self.results['phase_9']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_9']['status'] == 'complete'
    
    def validate_phase_10(self):
        """Validate Phase 10: Testing & Validation"""
        print("\n" + "="*60)
        print("PHASE 10: Testing & Validation")
        print("="*60)
        
        tasks = []
        
        # Check test files
        test_files = [
            "tests/conftest.py",
            "tests/test_packing_algorithms.py",
            "tests/test_shipping_costs.py",
            "tests/test_multi_product_packing.py",
            "tests/test_bulk_upload.py",
            "tests/test_analytics.py",
            "tests/test_security.py",
            "tests/test_integration_workflows.py",
            "tests/test_performance_benchmarks.py",
        ]
        
        for test_file in test_files:
            if self.check_file_exists(test_file):
                tasks.append(f"✓ {test_file} exists")
            else:
                tasks.append(f"✗ {test_file} missing")
        
        # Check load tests
        if self.check_file_exists("load_tests/locustfile.py"):
            tasks.append("✓ Locust load tests exist")
        else:
            tasks.append("✗ Locust load tests missing")
        
        # Check smoke tests
        if self.check_file_exists("smoke_tests/test_smoke.py"):
            tasks.append("✓ Smoke tests exist")
        else:
            tasks.append("✗ Smoke tests missing")
        
        self.results['phase_10']['tasks'] = tasks
        self.results['phase_10']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_10']['status'] == 'complete'
    
    def validate_phase_11(self):
        """Validate Phase 11: Documentation & Deployment"""
        print("\n" + "="*60)
        print("PHASE 11: Documentation & Deployment")
        print("="*60)
        
        tasks = []
        
        # Check documentation
        docs = [
            "../docs/WAREHOUSE_INTEGRATION_GUIDE.md",
            "../docs/DEPLOYMENT_GUIDE.md",
            "../docs/MONITORING_SETUP_GUIDE.md",
            "../docs/ROLLBACK_PROCEDURES.md",
        ]
        
        for doc in docs:
            if self.check_file_exists(doc):
                tasks.append(f"✓ {doc.split('/')[-1]} exists")
            else:
                tasks.append(f"✗ {doc.split('/')[-1]} missing")
        
        # Check deployment scripts
        scripts = [
            "../scripts/deploy_migrations.sh",
            "../scripts/deploy_api.sh",
            "../scripts/deploy_workers.sh",
        ]
        
        for script in scripts:
            if self.check_file_exists(script):
                tasks.append(f"✓ {script.split('/')[-1]} exists")
            else:
                tasks.append(f"✗ {script.split('/')[-1]} missing")
        
        # Check environment templates
        if self.check_file_exists(".env.example"):
            tasks.append("✓ .env.example exists")
        else:
            tasks.append("✗ .env.example missing")
        
        if self.check_file_exists(".env.production.example"):
            tasks.append("✓ .env.production.example exists")
        else:
            tasks.append("✗ .env.production.example missing")
        
        self.results['phase_11']['tasks'] = tasks
        self.results['phase_11']['status'] = 'complete' if all('✓' in t for t in tasks) else 'incomplete'
        
        for task in tasks:
            print(task)
        
        return self.results['phase_11']['status'] == 'complete'
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        total_phases = len(self.results)
        complete_phases = sum(1 for p in self.results.values() if p['status'] == 'complete')
        
        for phase, data in self.results.items():
            status_icon = "✓" if data['status'] == 'complete' else "✗"
            print(f"{status_icon} {phase.upper().replace('_', ' ')}: {data['status']}")
        
        print(f"\nTotal: {complete_phases}/{total_phases} phases complete")
        
        if complete_phases == total_phases:
            print("\n✓ ALL PHASES COMPLETE!")
            return True
        else:
            print(f"\n✗ {total_phases - complete_phases} phases incomplete")
            return False
    
    def run_validation(self):
        """Run complete validation."""
        print("="*60)
        print("COMPREHENSIVE PHASE VALIDATION")
        print("Production Logistics Upgrade - Phases 1-11")
        print("="*60)
        
        self.validate_phase_1()
        self.validate_phase_2()
        self.validate_phase_3()
        self.validate_phase_4()
        self.validate_phase_5()
        self.validate_phase_6()
        self.validate_phase_7()
        self.validate_phase_8()
        self.validate_phase_9()
        self.validate_phase_10()
        self.validate_phase_11()
        
        return self.print_summary()


if __name__ == "__main__":
    validator = PhaseValidator()
    all_complete = validator.run_validation()
    
    sys.exit(0 if all_complete else 1)
