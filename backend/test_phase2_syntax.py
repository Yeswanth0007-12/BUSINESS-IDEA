"""
Test script for Phase 2 - Syntax and Structure Check
Tests all service files for syntax errors without importing dependencies
"""

import os
import py_compile
import sys

def test_file_syntax(filepath):
    """Test if a Python file has valid syntax"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """Run syntax tests on all Phase 2 files"""
    print("\n" + "=" * 60)
    print("PHASE 2 SYNTAX TESTING - Backend Services")
    print("=" * 60 + "\n")
    
    # Files to test
    files_to_test = [
        ("Core Security", "app/core/security.py"),
        ("Core JWT", "app/core/jwt.py"),
        ("Auth Service", "app/services/auth_service.py"),
        ("Optimization Engine", "app/services/optimization_engine.py"),
        ("Product Service", "app/services/product_service.py"),
        ("Box Service", "app/services/box_service.py"),
        ("Analytics Service", "app/services/analytics_service.py"),
        ("History Service", "app/services/history_service.py"),
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
    
    # Check file structure
    print("\nChecking Service File Structure...")
    print("=" * 60)
    
    structure_checks = []
    
    for name, filepath in files_to_test:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for class definition (except core modules)
                if 'Service' in name or 'Engine' in name:
                    if 'class ' in content:
                        print(f"✓ {name}: Has class definition")
                        structure_checks.append(True)
                    else:
                        print(f"✗ {name}: Missing class definition")
                        structure_checks.append(False)
                else:
                    # Core modules should have functions
                    if 'def ' in content:
                        print(f"✓ {name}: Has function definitions")
                        structure_checks.append(True)
                    else:
                        print(f"✗ {name}: Missing function definitions")
                        structure_checks.append(False)
    
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
        print("\n⚠️  PHASE 2 SYNTAX TEST FAILED")
        return 1
    else:
        print("\n✅ ALL PHASE 2 SYNTAX TESTS PASSED!")
        print("All service files have valid Python syntax.")
        print("\nNote: Runtime tests require dependencies to be installed.")
        print("To install: pip install -r requirements.txt\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
