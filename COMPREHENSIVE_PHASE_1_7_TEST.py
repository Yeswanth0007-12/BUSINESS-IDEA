#!/usr/bin/env python3
"""
Comprehensive Test Suite: Phases 1-7
Tests all completed phases to ensure everything works correctly
"""

import os
import sys

def test_file_exists(filepath):
    """Test if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {filepath}")
    return exists

def test_file_contains(filepath, search_strings):
    """Test if file contains specific strings"""
    if not os.path.exists(filepath):
        print(f"✗ {filepath} does not exist")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for search_str in search_strings:
        if search_str in content:
            print(f"  ✓ Contains '{search_str}'")
        else:
            print(f"  ✗ Missing '{search_str}'")
            all_found = False
    
    return all_found

def main():
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE: PHASES 1-7")
    print("=" * 70)
    
    phase_results = {}
    
    # ========== PHASE 1: Project Setup & Database Foundation ==========
    print("\n" + "=" * 70)
    print("PHASE 1: Project Setup & Database Foundation")
    print("=" * 70)
    
    phase1_tests = []
    
    print("\n--- Backend Structure ---")
    phase1_tests.append(test_file_exists('backend/requirements.txt'))
    phase1_tests.append(test_file_exists('backend/app/main.py'))
    phase1_tests.append(test_file_exists('backend/app/core/config.py'))
    phase1_tests.append(test_file_exists('backend/app/core/database.py'))
    phase1_tests.append(test_file_exists('backend/.env.example'))
    
    print("\n--- Frontend Structure ---")
    phase1_tests.append(test_file_exists('frontend/package.json'))
    phase1_tests.append(test_file_exists('frontend/src/main.tsx'))
    phase1_tests.append(test_file_exists('frontend/src/services/api.ts'))
    phase1_tests.append(test_file_exists('frontend/tailwind.config.js'))
    
    print("\n--- Database Models ---")
    phase1_tests.append(test_file_exists('backend/app/models/company.py'))
    phase1_tests.append(test_file_exists('backend/app/models/user.py'))
    phase1_tests.append(test_file_exists('backend/app/models/product.py'))
    phase1_tests.append(test_file_exists('backend/app/models/box.py'))
    phase1_tests.append(test_file_exists('backend/app/models/optimization_run.py'))
    phase1_tests.append(test_file_exists('backend/app/models/optimization_result.py'))
    
    print("\n--- Alembic Configuration ---")
    phase1_tests.append(test_file_exists('backend/alembic.ini'))
    phase1_tests.append(test_file_exists('backend/alembic/env.py'))
    phase1_tests.append(test_file_exists('backend/alembic/versions/001_initial_migration.py'))
    
    phase_results['Phase 1'] = all(phase1_tests)
    
    # ========== PHASE 2: Backend Services & Business Logic ==========
    print("\n" + "=" * 70)
    print("PHASE 2: Backend Services & Business Logic")
    print("=" * 70)
    
    phase2_tests = []
    
    print("\n--- Pydantic Schemas ---")
    phase2_tests.append(test_file_exists('backend/app/schemas/user.py'))
    phase2_tests.append(test_file_exists('backend/app/schemas/product.py'))
    phase2_tests.append(test_file_exists('backend/app/schemas/box.py'))
    phase2_tests.append(test_file_exists('backend/app/schemas/optimization.py'))
    phase2_tests.append(test_file_exists('backend/app/schemas/analytics.py'))
    
    print("\n--- Services ---")
    phase2_tests.append(test_file_exists('backend/app/services/auth_service.py'))
    phase2_tests.append(test_file_exists('backend/app/services/optimization_engine.py'))
    phase2_tests.append(test_file_exists('backend/app/services/product_service.py'))
    phase2_tests.append(test_file_exists('backend/app/services/box_service.py'))
    phase2_tests.append(test_file_exists('backend/app/services/analytics_service.py'))
    phase2_tests.append(test_file_exists('backend/app/services/history_service.py'))
    
    print("\n--- Security ---")
    phase2_tests.append(test_file_exists('backend/app/core/security.py'))
    phase2_tests.append(test_file_exists('backend/app/core/jwt.py'))
    
    phase_results['Phase 2'] = all(phase2_tests)
    
    # ========== PHASE 3: Backend API Endpoints ==========
    print("\n" + "=" * 70)
    print("PHASE 3: Backend API Endpoints")
    print("=" * 70)
    
    phase3_tests = []
    
    print("\n--- API Endpoints ---")
    phase3_tests.append(test_file_exists('backend/app/api/auth.py'))
    phase3_tests.append(test_file_exists('backend/app/api/products.py'))
    phase3_tests.append(test_file_exists('backend/app/api/boxes.py'))
    phase3_tests.append(test_file_exists('backend/app/api/optimization.py'))
    phase3_tests.append(test_file_exists('backend/app/api/analytics.py'))
    phase3_tests.append(test_file_exists('backend/app/api/history.py'))
    
    print("\n--- Main App Integration ---")
    print("Checking main.py for router mounts...")
    phase3_tests.append(test_file_contains('backend/app/main.py', [
        'auth_router',
        'products_router',
        'boxes_router',
        'optimization_router',
        'analytics_router',
        'history_router'
    ]))
    
    phase_results['Phase 3'] = all(phase3_tests)
    
    # ========== PHASE 4: Backend Middleware & Security ==========
    print("\n" + "=" * 70)
    print("PHASE 4: Backend Middleware & Security")
    print("=" * 70)
    
    phase4_tests = []
    
    print("\n--- Middleware ---")
    phase4_tests.append(test_file_exists('backend/app/middleware/security.py'))
    phase4_tests.append(test_file_exists('backend/app/middleware/rate_limit.py'))
    phase4_tests.append(test_file_exists('backend/app/middleware/error_handler.py'))
    
    print("\n--- CORS Configuration ---")
    print("Checking main.py for CORS middleware...")
    phase4_tests.append(test_file_contains('backend/app/main.py', [
        'CORSMiddleware',
        'allow_origins',
        'allow_credentials'
    ]))
    
    phase_results['Phase 4'] = all(phase4_tests)
    
    # ========== PHASE 5: Frontend Infrastructure ==========
    print("\n" + "=" * 70)
    print("PHASE 5: Frontend Infrastructure")
    print("=" * 70)
    
    phase5_tests = []
    
    print("\n--- API Client ---")
    print("Checking api.ts for endpoints...")
    phase5_tests.append(test_file_contains('frontend/src/services/api.ts', [
        'login',
        'register',
        'getProducts',
        'createProduct',
        'getBoxes',
        'runOptimization',
        'getDashboard'
    ]))
    
    print("\n--- Authentication Context ---")
    phase5_tests.append(test_file_exists('frontend/src/contexts/AuthContext.tsx'))
    print("Checking AuthContext for methods...")
    phase5_tests.append(test_file_contains('frontend/src/contexts/AuthContext.tsx', [
        'AuthProvider',
        'useAuth',
        'login',
        'logout',
        'isAuthenticated'
    ]))
    
    print("\n--- Protected Route ---")
    phase5_tests.append(test_file_exists('frontend/src/components/ProtectedRoute.tsx'))
    
    print("\n--- Router Configuration ---")
    print("Checking App.tsx for routes...")
    phase5_tests.append(test_file_contains('frontend/src/App.tsx', [
        'BrowserRouter',
        'Routes',
        'Route',
        'ProtectedRoute'
    ]))
    
    phase_results['Phase 5'] = all(phase5_tests)
    
    # ========== PHASE 6: Frontend Pages ==========
    print("\n" + "=" * 70)
    print("PHASE 6: Frontend Pages")
    print("=" * 70)
    
    phase6_tests = []
    
    print("\n--- Pages ---")
    phase6_tests.append(test_file_exists('frontend/src/pages/LoginPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/RegisterPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/DashboardPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/ProductsPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/BoxesPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/OptimizePage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/HistoryPage.tsx'))
    phase6_tests.append(test_file_exists('frontend/src/pages/LeakagePage.tsx'))
    
    print("\n--- Dashboard Features ---")
    print("Checking DashboardPage for KPI cards and charts...")
    phase6_tests.append(test_file_contains('frontend/src/pages/DashboardPage.tsx', [
        'DashboardMetrics',
        'LineChart',
        'total_products',
        'total_savings'
    ]))
    
    print("\n--- Products Page Features ---")
    print("Checking ProductsPage for CRUD operations...")
    phase6_tests.append(test_file_contains('frontend/src/pages/ProductsPage.tsx', [
        'createProduct',
        'updateProduct',
        'deleteProduct',
        'showModal'
    ]))
    
    phase_results['Phase 6'] = all(phase6_tests)
    
    # ========== PHASE 7: Frontend Components ==========
    print("\n" + "=" * 70)
    print("PHASE 7: Frontend Components")
    print("=" * 70)
    
    phase7_tests = []
    
    print("\n--- Components ---")
    phase7_tests.append(test_file_exists('frontend/src/layout/Sidebar.tsx'))
    phase7_tests.append(test_file_exists('frontend/src/components/KPICard.tsx'))
    phase7_tests.append(test_file_exists('frontend/src/components/DataTable.tsx'))
    phase7_tests.append(test_file_exists('frontend/src/components/Modal.tsx'))
    phase7_tests.append(test_file_exists('frontend/src/components/LoadingSpinner.tsx'))
    
    print("\n--- Sidebar Features ---")
    print("Checking Sidebar for navigation...")
    phase7_tests.append(test_file_contains('frontend/src/layout/Sidebar.tsx', [
        'Dashboard',
        'Products',
        'Boxes',
        'Optimize',
        'History',
        'Leakage',
        'useLocation',
        'logout'
    ]))
    
    print("\n--- KPI Card Features ---")
    print("Checking KPICard for props...")
    phase7_tests.append(test_file_contains('frontend/src/components/KPICard.tsx', [
        'KPICardProps',
        'title',
        'value',
        'icon',
        'trend'
    ]))
    
    print("\n--- Data Table Features ---")
    print("Checking DataTable for sorting and actions...")
    phase7_tests.append(test_file_contains('frontend/src/components/DataTable.tsx', [
        'DataTableProps',
        'sortable',
        'onEdit',
        'onDelete',
        'handleSort'
    ]))
    
    print("\n--- Modal Features ---")
    print("Checking Modal for functionality...")
    phase7_tests.append(test_file_contains('frontend/src/components/Modal.tsx', [
        'ModalProps',
        'isOpen',
        'onClose',
        'Escape',
        'backdrop-blur'
    ]))
    
    print("\n--- App Integration ---")
    print("Checking App.tsx for Sidebar integration...")
    phase7_tests.append(test_file_contains('frontend/src/App.tsx', [
        'import Sidebar',
        '<Sidebar />',
        'isAuthPage'
    ]))
    
    phase_results['Phase 7'] = all(phase7_tests)
    
    # ========== SUMMARY ==========
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for phase, passed in phase_results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{phase}: {status}")
    
    all_passed = all(phase_results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL PHASES (1-7) PASSED - Ready for Phase 8!")
    else:
        failed_phases = [p for p, passed in phase_results.items() if not passed]
        print(f"✗ FAILED PHASES: {', '.join(failed_phases)}")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
