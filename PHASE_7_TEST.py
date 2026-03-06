#!/usr/bin/env python3
"""
Phase 7 Test Suite: Frontend Components
Tests all Phase 7 components and integration
"""

import os
import sys
import subprocess

def test_file_exists(filepath):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath} exists")
        return True
    else:
        print(f"✗ {filepath} missing")
        return False

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
            print(f"✓ {filepath} contains '{search_str}'")
        else:
            print(f"✗ {filepath} missing '{search_str}'")
            all_found = False
    
    return all_found

def run_build_test():
    """Test if frontend builds successfully"""
    print("\n=== Testing Frontend Build ===")
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd='frontend',
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✓ Frontend builds successfully")
            return True
        else:
            print(f"✗ Frontend build failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Build test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("PHASE 7 TEST SUITE: Frontend Components")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Sidebar Component
    print("\n=== Test 1: Sidebar Component ===")
    tests_total += 1
    sidebar_checks = [
        test_file_exists('frontend/src/layout/Sidebar.tsx'),
        test_file_contains('frontend/src/layout/Sidebar.tsx', [
            'useLocation',
            'navigation',
            'Dashboard',
            'Products',
            'Boxes',
            'Optimize',
            'History',
            'Leakage',
            'logout',
            'bg-blue-600'
        ])
    ]
    if all(sidebar_checks):
        tests_passed += 1
        print("✓ Test 1 PASSED")
    else:
        print("✗ Test 1 FAILED")
    
    # Test 2: KPI Card Component
    print("\n=== Test 2: KPI Card Component ===")
    tests_total += 1
    kpi_checks = [
        test_file_exists('frontend/src/components/KPICard.tsx'),
        test_file_contains('frontend/src/components/KPICard.tsx', [
            'interface KPICardProps',
            'title',
            'value',
            'icon',
            'iconColor',
            'trend',
            'isPositive',
            'bg-slate-800'
        ])
    ]
    if all(kpi_checks):
        tests_passed += 1
        print("✓ Test 2 PASSED")
    else:
        print("✗ Test 2 FAILED")
    
    # Test 3: Data Table Component
    print("\n=== Test 3: Data Table Component ===")
    tests_total += 1
    table_checks = [
        test_file_exists('frontend/src/components/DataTable.tsx'),
        test_file_contains('frontend/src/components/DataTable.tsx', [
            'interface Column',
            'interface DataTableProps',
            'sortable',
            'onEdit',
            'onDelete',
            'sortKey',
            'sortOrder',
            'handleSort',
            'emptyMessage'
        ])
    ]
    if all(table_checks):
        tests_passed += 1
        print("✓ Test 3 PASSED")
    else:
        print("✗ Test 3 FAILED")
    
    # Test 4: Modal Component
    print("\n=== Test 4: Modal Component ===")
    tests_total += 1
    modal_checks = [
        test_file_exists('frontend/src/components/Modal.tsx'),
        test_file_contains('frontend/src/components/Modal.tsx', [
            'interface ModalProps',
            'isOpen',
            'onClose',
            'title',
            'children',
            'maxWidth',
            'useEffect',
            'Escape',
            'backdrop-blur',
            'stopPropagation'
        ])
    ]
    if all(modal_checks):
        tests_passed += 1
        print("✓ Test 4 PASSED")
    else:
        print("✗ Test 4 FAILED")
    
    # Test 5: Loading Spinner Component
    print("\n=== Test 5: Loading Spinner Component ===")
    tests_total += 1
    spinner_checks = [
        test_file_exists('frontend/src/components/LoadingSpinner.tsx'),
        test_file_contains('frontend/src/components/LoadingSpinner.tsx', [
            'interface LoadingSpinnerProps',
            'size',
            'message',
            'fullScreen',
            'small',
            'medium',
            'large',
            'animate-spin'
        ])
    ]
    if all(spinner_checks):
        tests_passed += 1
        print("✓ Test 5 PASSED")
    else:
        print("✗ Test 5 FAILED")
    
    # Test 6: App.tsx Integration
    print("\n=== Test 6: App.tsx Integration ===")
    tests_total += 1
    app_checks = [
        test_file_contains('frontend/src/App.tsx', [
            'import Sidebar',
            'useLocation',
            'isAuthPage',
            '<Sidebar />',
            'flex'
        ])
    ]
    if all(app_checks):
        tests_passed += 1
        print("✓ Test 6 PASSED")
    else:
        print("✗ Test 6 FAILED")
    
    # Test 7: Build Test
    print("\n=== Test 7: Build Test ===")
    tests_total += 1
    if run_build_test():
        tests_passed += 1
        print("✓ Test 7 PASSED")
    else:
        print("✗ Test 7 FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"PHASE 7 TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ ALL TESTS PASSED - Phase 7 Complete!")
        return 0
    else:
        print(f"✗ {tests_total - tests_passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
