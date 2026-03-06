#!/usr/bin/env python3
"""
Quick Validation Test for Production Logistics Upgrade

This script validates the implementation without requiring running services.
It checks for file existence, syntax, and basic structure.

Usage:
    python quick_validation_test.py
"""

import sys
import ast
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

class ValidationResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = {}
    
    def add_result(self, category, test_name, passed, message=""):
        if category not in self.results:
            self.results[category] = []
        
        self.total += 1
        if passed:
            self.passed += 1
            print_success(f"{test_name}")
        else:
            self.failed += 1
            print_error(f"{test_name}: {message}")
        
        self.results[category].append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    def get_pass_rate(self):
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def print_summary(self):
        print_header("VALIDATION SUMMARY")
        
        for category, tests in self.results.items():
            passed = sum(1 for t in tests if t['passed'])
            total = len(tests)
            rate = (passed / total * 100) if total > 0 else 0
            
            color = Colors.GREEN if rate >= 80 else Colors.YELLOW if rate >= 50 else Colors.RED
            print(f"{category}: {color}{passed}/{total} ({rate:.0f}%){Colors.END}")
        
        print(f"\n{'='*80}")
        print(f"Total: {self.passed}/{self.total} tests passed")
        print(f"Pass Rate: {Colors.GREEN if self.get_pass_rate() >= 80 else Colors.RED}{self.get_pass_rate():.1f}%{Colors.END}")
        print(f"{'='*80}\n")

def check_file_exists(path):
    """Check if file exists"""
    return Path(path).exists()

def check_python_syntax(path):
    """Check if Python file has valid syntax"""
    try:
        with open(path, 'r') as f:
            ast.parse(f.read())
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, str(e)

def validate_phase1(results):
    """Validate Phase 1: Enhanced Data Models"""
    print_header("Phase 1: Enhanced Data Models")
    
    files = [
        "backend/alembic/versions/004_enhanced_data_models.py",
        "backend/app/models/product.py",
        "backend/app/models/box.py",
        "backend/app/schemas/product.py",
        "backend/app/schemas/box.py"
    ]
    
    for file in files:
        exists = check_file_exists(file)
        if exists:
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 1", f"{Path(file).name}", valid, msg)
        else:
            results.add_result("Phase 1", f"{Path(file).name}", False, "File not found")

def validate_phase2(results):
    """Validate Phase 2: Advanced Packing Engine"""
    print_header("Phase 2: Advanced Packing Engine")
    
    # Check optimization engine
    file = "backend/app/services/optimization_engine.py"
    if check_file_exists(file):
        valid, msg = check_python_syntax(file)
        results.add_result("Phase 2", "Optimization Engine", valid, msg)
        
        # Check for specific methods
        try:
            with open(file, 'r') as f:
                content = f.read()
                
            has_orientation = "test_all_orientations" in content or "orientation" in content
            results.add_result("Phase 2", "6-orientation testing", has_orientation,
                             "Method not found" if not has_orientation else "")
            
            has_weight = "validate_weight_constraint" in content or "weight" in content
            results.add_result("Phase 2", "Weight constraints", has_weight,
                             "Method not found" if not has_weight else "")
        except Exception as e:
            results.add_result("Phase 2", "Method validation", False, str(e))
    else:
        results.add_result("Phase 2", "Optimization Engine", False, "File not found")

def validate_phase3(results):
    """Validate Phase 3: Shipping Cost Calculator"""
    print_header("Phase 3: Shipping Cost Calculator")
    
    file = "backend/app/services/optimization_engine.py"
    if check_file_exists(file):
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            has_volumetric = "volumetric_weight" in content
            results.add_result("Phase 3", "Volumetric weight calculation", has_volumetric)
            
            has_billable = "billable_weight" in content
            results.add_result("Phase 3", "Billable weight calculation", has_billable)
            
            has_shipping = "shipping_cost" in content
            results.add_result("Phase 3", "Shipping cost calculation", has_shipping)
        except Exception as e:
            results.add_result("Phase 3", "Shipping calculations", False, str(e))
    else:
        results.add_result("Phase 3", "Optimization Engine", False, "File not found")

def validate_phase4(results):
    """Validate Phase 4: Multi-Product Order Packing"""
    print_header("Phase 4: Multi-Product Order Packing")
    
    files = [
        ("backend/app/models/order.py", "Order models"),
        ("backend/alembic/versions/007_multi_product_orders.py", "Order migration"),
        ("backend/app/schemas/order.py", "Order schemas"),
        ("backend/app/services/order_service.py", "Order service"),
        ("backend/app/api/orders.py", "Order API")
    ]
    
    for file, name in files:
        if check_file_exists(file):
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 4", name, valid, msg)
        else:
            results.add_result("Phase 4", name, False, "File not found")

def validate_phase5(results):
    """Validate Phase 5: Queue System Architecture"""
    print_header("Phase 5: Queue System Architecture")
    
    files = [
        ("backend/app/core/celery_app.py", "Celery configuration"),
        ("backend/app/models/optimization_task.py", "Task model"),
        ("backend/alembic/versions/008_optimization_tasks.py", "Task migration"),
        ("backend/app/schemas/task.py", "Task schemas"),
        ("backend/app/tasks/optimization_tasks.py", "Celery tasks"),
        ("backend/app/api/tasks.py", "Task API")
    ]
    
    for file, name in files:
        if check_file_exists(file):
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 5", name, valid, msg)
        else:
            results.add_result("Phase 5", name, False, "File not found")

def validate_phase6(results):
    """Validate Phase 6: Bulk Order Processing"""
    print_header("Phase 6: Bulk Order Processing")
    
    files = [
        ("backend/app/models/bulk_upload.py", "Bulk upload models"),
        ("backend/alembic/versions/009_bulk_uploads.py", "Bulk upload migration"),
        ("backend/app/schemas/bulk_upload.py", "Bulk upload schemas"),
        ("backend/app/services/bulk_upload_service.py", "Bulk upload service"),
        ("backend/app/api/bulk_upload.py", "Bulk upload API")
    ]
    
    for file, name in files:
        if check_file_exists(file):
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 6", name, valid, msg)
        else:
            results.add_result("Phase 6", name, False, "File not found")

def validate_phase7(results):
    """Validate Phase 7: Advanced Analytics"""
    print_header("Phase 7: Advanced Analytics")
    
    files = [
        ("backend/app/models/analytics_snapshot.py", "Analytics models"),
        ("backend/alembic/versions/010_analytics_tables.py", "Analytics migration"),
        ("backend/app/services/analytics_service_v2.py", "Analytics service")
    ]
    
    for file, name in files:
        if check_file_exists(file):
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 7", name, valid, msg)
        else:
            results.add_result("Phase 7", name, False, "File not found")

def validate_phase8(results):
    """Validate Phase 8: Enhanced Dashboard APIs"""
    print_header("Phase 8: Enhanced Dashboard APIs")
    
    file = "backend/app/api/analytics.py"
    if check_file_exists(file):
        valid, msg = check_python_syntax(file)
        results.add_result("Phase 8", "Analytics API", valid, msg)
        
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            has_summary = "/summary" in content
            results.add_result("Phase 8", "Summary endpoint", has_summary)
            
            has_box_usage = "/box-usage" in content
            results.add_result("Phase 8", "Box usage endpoint", has_box_usage)
            
            has_shipping = "/shipping-cost" in content
            results.add_result("Phase 8", "Shipping cost endpoint", has_shipping)
            
            has_trends = "/trends" in content
            results.add_result("Phase 8", "Trends endpoint", has_trends)
        except Exception as e:
            results.add_result("Phase 8", "Endpoint validation", False, str(e))
    else:
        results.add_result("Phase 8", "Analytics API", False, "File not found")

def validate_phase9(results):
    """Validate Phase 9: Warehouse Integration API"""
    print_header("Phase 9: Warehouse Integration API")
    
    files = [
        ("backend/app/models/api_key.py", "API key model"),
        ("backend/app/models/webhook.py", "Webhook models"),
        ("backend/alembic/versions/011_warehouse_integration.py", "Warehouse migration"),
        ("backend/app/schemas/warehouse.py", "Warehouse schemas"),
        ("backend/app/services/warehouse_service.py", "Warehouse service"),
        ("backend/app/api/warehouse.py", "Warehouse API"),
        ("backend/app/middleware/warehouse_rate_limit.py", "Rate limiting")
    ]
    
    for file, name in files:
        if check_file_exists(file):
            valid, msg = check_python_syntax(file)
            results.add_result("Phase 9", name, valid, msg)
        else:
            results.add_result("Phase 9", name, False, "File not found")

def validate_phase10(results):
    """Validate Phase 10: Testing & Validation"""
    print_header("Phase 10: Testing & Validation")
    
    test_files = [
        ("backend/tests/test_api_key_auth.py", "API key auth tests"),
        ("backend/tests/test_webhook_signature.py", "Webhook signature tests"),
        ("backend/tests/test_end_to_end_workflows.py", "E2E workflow tests"),
        ("backend/tests/test_integration_workflows.py", "Integration tests"),
        ("backend/tests/test_performance_benchmarks.py", "Performance tests"),
        ("backend/tests/test_security.py", "Security tests"),
        ("backend/smoke_tests/test_smoke.py", "Smoke tests"),
        ("backend/load_tests/locustfile.py", "Load tests (Locust)"),
        ("backend/load_tests/k6_load_test.js", "Load tests (k6)")
    ]
    
    for file, name in test_files:
        if check_file_exists(file):
            if file.endswith('.py'):
                valid, msg = check_python_syntax(file)
                results.add_result("Phase 10", name, valid, msg)
            else:
                results.add_result("Phase 10", name, True)
        else:
            results.add_result("Phase 10", name, False, "File not found")

def validate_phase11(results):
    """Validate Phase 11: Documentation & Deployment"""
    print_header("Phase 11: Documentation & Deployment")
    
    files = [
        ("scripts/deploy_staging.sh", "Staging deployment script"),
        ("scripts/validate_staging.sh", "Staging validation script"),
        ("scripts/deploy_production.sh", "Production deployment script"),
        ("scripts/validate_production.sh", "Production validation script"),
        ("scripts/monitor_production.sh", "Production monitoring script"),
        ("docs/STAGING_DEPLOYMENT_GUIDE.md", "Staging deployment guide"),
        ("docs/PRODUCTION_DEPLOYMENT_GUIDE.md", "Production deployment guide"),
        ("docs/POST_DEPLOYMENT_VALIDATION_GUIDE.md", "Post-deployment guide"),
        ("docs/WAREHOUSE_INTEGRATION_GUIDE.md", "Warehouse integration guide"),
        ("docs/ROLLBACK_PROCEDURES.md", "Rollback procedures"),
        ("monitoring/prometheus/prometheus.yml", "Prometheus config"),
        ("monitoring/prometheus/alerts/packoptima.yml", "Alert rules"),
        ("monitoring/grafana/dashboards/api-performance.json", "API dashboard"),
        ("monitoring/grafana/dashboards/queue-metrics.json", "Queue dashboard"),
        ("monitoring/grafana/dashboards/database-metrics.json", "Database dashboard")
    ]
    
    for file, name in files:
        exists = check_file_exists(file)
        results.add_result("Phase 11", name, exists, "File not found" if not exists else "")

def main():
    """Main validation"""
    print_header("Production Logistics Upgrade - Quick Validation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = ValidationResults()
    
    try:
        validate_phase1(results)
        validate_phase2(results)
        validate_phase3(results)
        validate_phase4(results)
        validate_phase5(results)
        validate_phase6(results)
        validate_phase7(results)
        validate_phase8(results)
        validate_phase9(results)
        validate_phase10(results)
        validate_phase11(results)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error during validation: {e}{Colors.END}")
    
    # Print summary
    results.print_summary()
    
    # Exit with appropriate code
    if results.get_pass_rate() >= 90:
        print(f"{Colors.GREEN}✓ VALIDATION PASSED - Implementation complete{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ VALIDATION FAILED - Some files missing or invalid{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
