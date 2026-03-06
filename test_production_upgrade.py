#!/usr/bin/env python3
"""
Comprehensive Test Suite for Production Logistics Upgrade

This script tests all implemented features and generates a pass rate report.
Run this after deploying to staging or production to validate the upgrade.

Usage:
    python test_production_upgrade.py
    
Requirements:
    - Docker containers running
    - Database migrated
    - Environment configured
"""

import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Color codes for output
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

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def run_command(cmd, cwd=None, timeout=60):
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []
    
    def add_result(self, category, test_name, passed, message="", skipped=False):
        self.total += 1
        if skipped:
            self.skipped += 1
            status = "SKIPPED"
        elif passed:
            self.passed += 1
            status = "PASSED"
        else:
            self.failed += 1
            status = "FAILED"
        
        self.results.append({
            "category": category,
            "test": test_name,
            "status": status,
            "message": message
        })
        
        if skipped:
            print_warning(f"{test_name}: SKIPPED - {message}")
        elif passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED - {message}")
    
    def get_pass_rate(self):
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def print_summary(self):
        print_header("TEST SUMMARY")
        print(f"Total Tests: {self.total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Skipped: {self.skipped}{Colors.END}")
        print(f"\nPass Rate: {Colors.GREEN if self.get_pass_rate() >= 80 else Colors.RED}{self.get_pass_rate():.1f}%{Colors.END}")
    
    def generate_report(self, filename="test_report.md"):
        """Generate markdown report"""
        with open(filename, 'w') as f:
            f.write("# Production Logistics Upgrade - Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {self.total}\n")
            f.write(f"- **Passed:** {self.passed}\n")
            f.write(f"- **Failed:** {self.failed}\n")
            f.write(f"- **Skipped:** {self.skipped}\n")
            f.write(f"- **Pass Rate:** {self.get_pass_rate():.1f}%\n\n")
            
            # Group by category
            categories = {}
            for result in self.results:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result)
            
            f.write("## Test Results by Category\n\n")
            for category, tests in categories.items():
                f.write(f"### {category}\n\n")
                f.write("| Test | Status | Message |\n")
                f.write("|------|--------|----------|\n")
                for test in tests:
                    status_icon = "✅" if test['status'] == "PASSED" else "❌" if test['status'] == "FAILED" else "⚠️"
                    f.write(f"| {test['test']} | {status_icon} {test['status']} | {test['message']} |\n")
                f.write("\n")
        
        print(f"\n{Colors.BLUE}Report generated: {filename}{Colors.END}")

def test_environment(results):
    """Test environment setup"""
    print_header("Phase 0: Environment Tests")
    
    # Check Docker
    success, _, _ = run_command("docker --version")
    results.add_result("Environment", "Docker installed", success)
    
    # Check Docker Compose
    success, _, _ = run_command("docker-compose --version")
    results.add_result("Environment", "Docker Compose installed", success)
    
    # Check Python
    success, _, _ = run_command("python --version")
    results.add_result("Environment", "Python installed", success)

def test_containers(results):
    """Test Docker containers"""
    print_header("Phase 1: Container Tests")
    
    containers = [
        "packoptima-api",
        "packoptima-db",
        "packoptima-redis",
        "packoptima-worker"
    ]
    
    for container in containers:
        success, stdout, _ = run_command(f"docker ps | grep {container}")
        results.add_result("Containers", f"{container} running", success)

def test_database(results):
    """Test database connectivity and migrations"""
    print_header("Phase 2: Database Tests")
    
    # Check database connectivity
    success, _, _ = run_command(
        "docker exec packoptima-db pg_isready -U postgres",
        timeout=10
    )
    results.add_result("Database", "PostgreSQL connectivity", success)
    
    # Check migrations
    success, stdout, stderr = run_command(
        "cd backend && alembic current",
        timeout=30
    )
    results.add_result("Database", "Alembic migrations applied", success, 
                      stdout.strip() if success else stderr.strip())

def test_api_health(results):
    """Test API health endpoints"""
    print_header("Phase 3: API Health Tests")
    
    import requests
    
    base_url = "http://localhost:8000"
    
    # Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        success = response.status_code == 200
        results.add_result("API Health", "Health endpoint", success,
                          f"Status: {response.status_code}")
    except Exception as e:
        results.add_result("API Health", "Health endpoint", False, str(e))
    
    # Docs endpoint
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        success = response.status_code == 200
        results.add_result("API Health", "API documentation", success,
                          f"Status: {response.status_code}")
    except Exception as e:
        results.add_result("API Health", "API documentation", False, str(e))
    
    # Metrics endpoint
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        success = response.status_code == 200
        results.add_result("API Health", "Metrics endpoint", success,
                          f"Status: {response.status_code}")
    except Exception as e:
        results.add_result("API Health", "Metrics endpoint", False, str(e))

def test_unit_tests(results):
    """Run unit tests"""
    print_header("Phase 4: Unit Tests")
    
    test_files = [
        "backend/tests/test_api_key_auth.py",
        "backend/tests/test_webhook_signature.py",
        "backend/tests/test_packing_algorithms.py",
        "backend/tests/test_shipping_costs.py",
        "backend/tests/test_multi_product_packing.py",
        "backend/tests/test_bulk_upload.py",
        "backend/tests/test_analytics.py",
        "backend/tests/test_security.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            test_name = Path(test_file).stem
            success, stdout, stderr = run_command(
                f"cd backend && python -m pytest {test_file} -v",
                timeout=60
            )
            
            # Parse pytest output for pass/fail count
            if success and "passed" in stdout:
                results.add_result("Unit Tests", test_name, True, "All tests passed")
            elif "passed" in stdout or "passed" in stderr:
                # Some tests passed
                results.add_result("Unit Tests", test_name, False, 
                                 "Some tests failed - check output")
            else:
                results.add_result("Unit Tests", test_name, False, 
                                 stderr.strip()[:100] if stderr else "Tests failed")
        else:
            results.add_result("Unit Tests", Path(test_file).stem, False, 
                             "Test file not found", skipped=True)

def test_integration(results):
    """Run integration tests"""
    print_header("Phase 5: Integration Tests")
    
    test_files = [
        "backend/tests/test_integration_workflows.py",
        "backend/tests/test_end_to_end_workflows.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            test_name = Path(test_file).stem
            success, stdout, stderr = run_command(
                f"cd backend && python -m pytest {test_file} -v",
                timeout=120
            )
            
            if success and "passed" in stdout:
                results.add_result("Integration Tests", test_name, True, "All tests passed")
            else:
                results.add_result("Integration Tests", test_name, False,
                                 "Some tests failed")
        else:
            results.add_result("Integration Tests", Path(test_file).stem, False,
                             "Test file not found", skipped=True)

def test_performance(results):
    """Test performance benchmarks"""
    print_header("Phase 6: Performance Tests")
    
    if Path("backend/tests/test_performance_benchmarks.py").exists():
        success, stdout, stderr = run_command(
            "cd backend && python -m pytest backend/tests/test_performance_benchmarks.py -v",
            timeout=120
        )
        results.add_result("Performance", "Performance benchmarks", success,
                          "Benchmarks completed" if success else "Benchmarks failed")
    else:
        results.add_result("Performance", "Performance benchmarks", False,
                          "Test file not found", skipped=True)

def test_security(results):
    """Run security tests"""
    print_header("Phase 7: Security Tests")
    
    # Multi-tenant isolation
    if Path("backend/security_tests/test_multi_tenant_isolation.py").exists():
        success, _, _ = run_command(
            "cd backend && python -m pytest security_tests/test_multi_tenant_isolation.py -v",
            timeout=60
        )
        results.add_result("Security", "Multi-tenant isolation", success)
    else:
        results.add_result("Security", "Multi-tenant isolation", False,
                          "Test file not found", skipped=True)
    
    # Security scan
    if Path("backend/security_tests/run_security_scan.sh").exists():
        success, _, _ = run_command(
            "bash backend/security_tests/run_security_scan.sh",
            timeout=120
        )
        results.add_result("Security", "Security scan", success)
    else:
        results.add_result("Security", "Security scan", False,
                          "Script not found", skipped=True)

def test_smoke(results):
    """Run smoke tests"""
    print_header("Phase 8: Smoke Tests")
    
    if Path("backend/smoke_tests/test_smoke.py").exists():
        success, _, _ = run_command(
            "cd backend && python -m pytest smoke_tests/test_smoke.py -v",
            timeout=60
        )
        results.add_result("Smoke Tests", "Smoke tests", success)
    else:
        results.add_result("Smoke Tests", "Smoke tests", False,
                          "Test file not found", skipped=True)

def test_monitoring(results):
    """Test monitoring infrastructure"""
    print_header("Phase 9: Monitoring Tests")
    
    import requests
    
    # Prometheus
    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=5)
        success = response.status_code == 200
        results.add_result("Monitoring", "Prometheus health", success)
    except Exception as e:
        results.add_result("Monitoring", "Prometheus health", False, str(e))
    
    # Grafana
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        success = response.status_code == 200
        results.add_result("Monitoring", "Grafana health", success)
    except Exception as e:
        results.add_result("Monitoring", "Grafana health", False, str(e))
    
    # AlertManager
    try:
        response = requests.get("http://localhost:9093/-/healthy", timeout=5)
        success = response.status_code == 200
        results.add_result("Monitoring", "AlertManager health", success)
    except Exception as e:
        results.add_result("Monitoring", "AlertManager health", False, str(e))

def main():
    """Main test execution"""
    print_header("Production Logistics Upgrade - Comprehensive Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = TestResults()
    
    try:
        # Run all test phases
        test_environment(results)
        test_containers(results)
        test_database(results)
        test_api_health(results)
        test_unit_tests(results)
        test_integration(results)
        test_performance(results)
        test_security(results)
        test_smoke(results)
        test_monitoring(results)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error during testing: {e}{Colors.END}")
    
    # Print summary
    results.print_summary()
    
    # Generate report
    results.generate_report("PRODUCTION_UPGRADE_TEST_REPORT.md")
    
    # Exit with appropriate code
    if results.get_pass_rate() >= 80:
        print(f"\n{Colors.GREEN}✓ Tests PASSED - Pass rate >= 80%{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}✗ Tests FAILED - Pass rate < 80%{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
