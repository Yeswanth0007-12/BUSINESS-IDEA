"""
Comprehensive test runner for all phases.
Runs syntax checks and basic validation for each phase.
"""
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print('='*70)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✓ {description} PASSED")
            if result.stdout:
                print(result.stdout[:500])  # Print first 500 chars
            return True
        else:
            print(f"✗ {description} FAILED")
            if result.stderr:
                print("Error output:")
                print(result.stderr[:1000])  # Print first 1000 chars
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {description} TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ {description} ERROR: {e}")
        return False

def main():
    """Run all phase tests"""
    print("="*70)
    print("COMPREHENSIVE PHASE TESTING")
    print("Production Logistics Upgrade - Phases 1-11")
    print("="*70)
    
    tests = []
    
    # Phase 1-4: Existing tests
    tests.append(("python test_phases_1_4_comprehensive.py", "Phases 1-4 Comprehensive Test"))
    
    # Phase 5: Queue system
    tests.append(("python test_phase5_queue.py", "Phase 5 Queue System Test"))
    
    # Phase 6: Bulk upload
    tests.append(("python test_phase6_bulk_upload.py", "Phase 6 Bulk Upload Test"))
    
    # Phase 7-8: Analytics
    tests.append(("python test_phase7_8.py", "Phases 7-8 Analytics Test"))
    
    # Phase 9: Warehouse integration
    tests.append(("python test_phase9_implementation.py", "Phase 9 Warehouse Integration Test"))
    
    # Syntax checks for all Python files
    print("\n" + "="*70)
    print("SYNTAX VALIDATION")
    print("="*70)
    
    python_files = [
        "app/models/api_key.py",
        "app/models/webhook.py",
        "app/schemas/warehouse.py",
        "app/services/warehouse_service.py",
        "app/api/warehouse.py",
        "app/middleware/warehouse_rate_limit.py",
    ]
    
    syntax_ok = True
    for pyfile in python_files:
        result = subprocess.run(
            f"python -m py_compile {pyfile}",
            shell=True,
            capture_output=True
        )
        if result.returncode == 0:
            print(f"✓ {pyfile} - syntax OK")
        else:
            print(f"✗ {pyfile} - syntax ERROR")
            syntax_ok = False
    
    if not syntax_ok:
        print("\n✗ SYNTAX ERRORS FOUND")
        return False
    
    print("\n✓ ALL SYNTAX CHECKS PASSED")
    
    # Run tests
    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {desc}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n✗ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
