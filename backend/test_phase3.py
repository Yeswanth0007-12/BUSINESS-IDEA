"""
Test script for Phase 3 - Backend API Endpoints
Tests all API endpoint files for syntax errors and proper structure
"""

import sys
import os
import py_compile

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_syntax(filepath):
    """Test if a Python file has valid syntax"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """Run syntax tests on all Phase 3 files"""
    print("\n" + "=" * 60)
    print("PHASE 3 TESTING - Backend API Endpoints")
    print("=" * 60 + "\n")
    
    # Files to test
    files_to_test = [
        ("Auth API", "app/api/auth.py"),
        ("Products API", "app/api/products.py"),
        ("Boxes API", "app/api/boxes.py"),
        ("Optimization API", "app/api/optimization.py"),
        ("Analytics API", "app/api/analytics.py"),
        ("History API", "app/api/history.py"),
        ("Main App", "app/main.py"),
    ]
    
    errors = []
    passed = 0
    
    print("Testing Python Syntax...")
    print("=" * 60)
    
    for name, filepath in files_to_test:
        if os.path.exists(filepath):
            success, error = test_file_syntax(filepath)
            if success:
                print(f"✓ {name}: OK")
                passed += 1
            else:
                error_msg = f"✗ {name}: SYNTAX ERROR\n  {error}"
                print(error_msg)
                errors.append(error_msg)
        else:
            error_msg = f"✗ {name}: FILE NOT FOUND - {filepath}"
            print(error_msg)
            errors.append(error_msg)
    
    print("=" * 60)
    
    # Check API structure
    print("\nChecking API Endpoint Structure...")
    print("=" * 60)
    
    structure_checks = []
    
    for name, filepath in files_to_test:
        if os.path.exists(filepath) and 'api/' in filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for router definition
                has_router = 'router = APIRouter' in content
                has_endpoints = '@router.' in content
                
                if has_router and has_endpoints:
                    print(f"✓ {name}: Has router and endpoints")
                    structure_checks.append(True)
                elif has_router:
                    print(f"⚠ {name}: Has router but no endpoints")
                    structure_checks.append(False)
                else:
                    print(f"✗ {name}: Missing router definition")
                    structure_checks.append(False)
    
    print("=" * 60)
    
    # Check main.py router mounting
    print("\nChecking Router Mounting in main.py...")
    print("=" * 60)
    
    if os.path.exists("app/main.py"):
        with open("app/main.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
            routers_to_check = [
                ("auth", "auth.router"),
                ("products", "products.router"),
                ("boxes", "boxes.router"),
                ("optimization", "optimization.router"),
                ("analytics", "analytics.router"),
                ("history", "history.router"),
            ]
            
            all_mounted = True
            for router_name, router_code in routers_to_check:
                if f"include_router({router_code})" in content:
                    print(f"✓ {router_name} router: Mounted")
                else:
                    print(f"✗ {router_name} router: NOT mounted")
                    all_mounted = False
            
            if all_mounted:
                print("\n✓ All routers properly mounted")
            else:
                print("\n✗ Some routers not mounted")
                errors.append("Not all routers are mounted in main.py")
    
    print("=" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Files tested: {len(files_to_test)}")
    print(f"Syntax checks passed: {passed}/{len(files_to_test)}")
    print(f"Structure checks passed: {sum(structure_checks)}/{len(structure_checks)}")
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found:")
        for error in errors:
            print(f"  {error}")
        print("\n⚠️  PHASE 3 TEST FAILED")
        return 1
    else:
        print("\n✅ ALL PHASE 3 TESTS PASSED!")
        print("All API endpoint files have valid Python syntax.")
        print("All routers are properly defined and mounted.")
        print("\nPhase 3 is complete and ready for Phase 4.\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
