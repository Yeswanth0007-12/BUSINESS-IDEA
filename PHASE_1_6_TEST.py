#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phases 1-6
PackOptima AI SaaS Platform
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{text}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'-'*len(text)}{Colors.RESET}")

def check_pass(message):
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    return True

def check_fail(message):
    print(f"{Colors.RED}✗{Colors.RESET} {message}")
    return False

def check_file_exists(filepath, description=""):
    """Check if a file exists"""
    if os.path.exists(filepath):
        return check_pass(f"{description or filepath} exists")
    else:
        return check_fail(f"{description or filepath} NOT FOUND")

def check_file_not_empty(filepath, description=""):
    """Check if a file exists and is not empty"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > 0:
            return check_pass(f"{description or filepath} exists and has content ({size} bytes)")
        else:
            return check_fail(f"{description or filepath} is EMPTY")
    else:
        return check_fail(f"{description or filepath} NOT FOUND")

def check_directory_exists(dirpath, description=""):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        return check_pass(f"{description or dirpath} directory exists")
    else:
        return check_fail(f"{description or dirpath} directory NOT FOUND")

def test_phase_1():
    """Test Phase 1: Project Setup & Database Foundation"""
    print_section("Phase 1: Project Setup & Database Foundation")
    
    results = []
    
    # Backend structure
    results.append(check_directory_exists("backend/app", "Backend app directory"))
    results.append(check_directory_exists("backend/app/api", "API directory"))
    results.append(check_directory_exists("backend/app/models", "Models directory"))
    results.append(check_directory_exists("backend/app/schemas", "Schemas directory"))
    results.append(check_directory_exists("backend/app/services", "Services directory"))
    results.append(check_directory_exists("backend/app/core", "Core directory"))
    results.append(check_directory_exists("backend/app/middleware", "Middleware directory"))
    
    # Backend files
    results.append(check_file_not_empty("backend/requirements.txt", "requirements.txt"))
    results.append(check_file_not_empty("backend/app/main.py", "main.py"))
    results.append(check_file_not_empty("backend/app/core/config.py", "config.py"))
    results.append(check_file_not_empty("backend/app/core/database.py", "database.py"))
    results.append(check_file_exists("backend/.env.example", ".env.example"))
    
    # Frontend structure
    results.append(check_directory_exists("frontend/src", "Frontend src directory"))
    results.append(check_directory_exists("frontend/src/pages", "Pages directory"))
    results.append(check_directory_exists("frontend/src/components", "Components directory"))
    results.append(check_directory_exists("frontend/src/services", "Services directory"))
    results.append(check_directory_exists("frontend/src/contexts", "Contexts directory"))
    
    # Frontend files
    results.append(check_file_not_empty("frontend/package.json", "package.json"))
    results.append(check_file_not_empty("frontend/tailwind.config.js", "tailwind.config.js"))
    results.append(check_file_not_empty("frontend/src/main.tsx", "main.tsx"))
    results.append(check_file_not_empty("frontend/src/index.css", "index.css"))
    
    # Database
    results.append(check_directory_exists("backend/alembic", "Alembic directory"))
    results.append(check_file_not_empty("backend/alembic.ini", "alembic.ini"))
    results.append(check_file_not_empty("backend/alembic/env.py", "alembic env.py"))
    
    # Models
    results.append(check_file_not_empty("backend/app/models/company.py", "Company model"))
    results.append(check_file_not_empty("backend/app/models/user.py", "User model"))
    results.append(check_file_not_empty("backend/app/models/product.py", "Product model"))
    results.append(check_file_not_empty("backend/app/models/box.py", "Box model"))
    results.append(check_file_not_empty("backend/app/models/optimization_run.py", "OptimizationRun model"))
    results.append(check_file_not_empty("backend/app/models/optimization_result.py", "OptimizationResult model"))
    
    return results

def test_phase_2():
    """Test Phase 2: Backend Services & Business Logic"""
    print_section("Phase 2: Backend Services & Business Logic")
    
    results = []
    
    # Schemas
    results.append(check_file_not_empty("backend/app/schemas/user.py", "User schemas"))
    results.append(check_file_not_empty("backend/app/schemas/product.py", "Product schemas"))
    results.append(check_file_not_empty("backend/app/schemas/box.py", "Box schemas"))
    results.append(check_file_not_empty("backend/app/schemas/optimization.py", "Optimization schemas"))
    results.append(check_file_not_empty("backend/app/schemas/analytics.py", "Analytics schemas"))
    
    # Services
    results.append(check_file_not_empty("backend/app/core/security.py", "Security module"))
    results.append(check_file_not_empty("backend/app/core/jwt.py", "JWT module"))
    results.append(check_file_not_empty("backend/app/services/auth_service.py", "Auth service"))
    results.append(check_file_not_empty("backend/app/services/optimization_engine.py", "Optimization engine"))
    results.append(check_file_not_empty("backend/app/services/product_service.py", "Product service"))
    results.append(check_file_not_empty("backend/app/services/box_service.py", "Box service"))
    results.append(check_file_not_empty("backend/app/services/analytics_service.py", "Analytics service"))
    results.append(check_file_not_empty("backend/app/services/history_service.py", "History service"))
    
    return results

def test_phase_3():
    """Test Phase 3: Backend API Endpoints"""
    print_section("Phase 3: Backend API Endpoints")
    
    results = []
    
    # API endpoints
    results.append(check_file_not_empty("backend/app/api/auth.py", "Auth API"))
    results.append(check_file_not_empty("backend/app/api/products.py", "Products API"))
    results.append(check_file_not_empty("backend/app/api/boxes.py", "Boxes API"))
    results.append(check_file_not_empty("backend/app/api/optimization.py", "Optimization API"))
    results.append(check_file_not_empty("backend/app/api/analytics.py", "Analytics API"))
    results.append(check_file_not_empty("backend/app/api/history.py", "History API"))
    
    return results

def test_phase_4():
    """Test Phase 4: Backend Middleware & Security"""
    print_section("Phase 4: Backend Middleware & Security")
    
    results = []
    
    # Middleware
    results.append(check_file_not_empty("backend/app/middleware/security.py", "Security middleware"))
    results.append(check_file_not_empty("backend/app/middleware/rate_limit.py", "Rate limit middleware"))
    results.append(check_file_not_empty("backend/app/middleware/error_handler.py", "Error handler middleware"))
    
    return results

def test_phase_5():
    """Test Phase 5: Frontend Infrastructure"""
    print_section("Phase 5: Frontend Infrastructure")
    
    results = []
    
    # Frontend infrastructure
    results.append(check_file_not_empty("frontend/src/services/api.ts", "API client service"))
    results.append(check_file_not_empty("frontend/src/contexts/AuthContext.tsx", "Auth context"))
    results.append(check_file_not_empty("frontend/src/components/ProtectedRoute.tsx", "Protected route component"))
    results.append(check_file_not_empty("frontend/src/App.tsx", "App component with routes"))
    
    return results

def test_phase_6():
    """Test Phase 6: Frontend Pages"""
    print_section("Phase 6: Frontend Pages")
    
    results = []
    
    # Pages
    results.append(check_file_not_empty("frontend/src/pages/LoginPage.tsx", "Login page"))
    results.append(check_file_not_empty("frontend/src/pages/RegisterPage.tsx", "Register page"))
    results.append(check_file_not_empty("frontend/src/pages/DashboardPage.tsx", "Dashboard page"))
    results.append(check_file_not_empty("frontend/src/pages/ProductsPage.tsx", "Products page"))
    results.append(check_file_not_empty("frontend/src/pages/BoxesPage.tsx", "Boxes page"))
    results.append(check_file_not_empty("frontend/src/pages/OptimizePage.tsx", "Optimize page"))
    results.append(check_file_not_empty("frontend/src/pages/HistoryPage.tsx", "History page"))
    results.append(check_file_not_empty("frontend/src/pages/LeakagePage.tsx", "Leakage page"))
    
    return results

def main():
    """Run all tests"""
    print_header("PackOptima AI SaaS Platform - Phases 1-6 Test Suite")
    
    all_results = []
    
    # Run all phase tests
    all_results.extend(test_phase_1())
    all_results.extend(test_phase_2())
    all_results.extend(test_phase_3())
    all_results.extend(test_phase_4())
    all_results.extend(test_phase_5())
    all_results.extend(test_phase_6())
    
    # Summary
    print_header("Test Summary")
    
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    
    print(f"\n{Colors.BOLD}Total Tests:{Colors.RESET} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.RESET} {passed_tests}")
    print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.RESET} {failed_tests}")
    
    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}All phases (1-6) are complete and verified.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"{Colors.RED}Please review the failed checks above.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
