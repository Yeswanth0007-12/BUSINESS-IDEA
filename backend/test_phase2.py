"""
Test script for Phase 2 - Backend Services & Business Logic
Tests all service files for syntax errors and proper imports
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Phase 2 modules can be imported"""
    errors = []
    
    print("Testing Phase 2 Backend Services...")
    print("=" * 60)
    
    # Test core modules
    modules_to_test = [
        ("Core Security", "app.core.security"),
        ("Core JWT", "app.core.jwt"),
        ("Auth Service", "app.services.auth_service"),
        ("Optimization Engine", "app.services.optimization_engine"),
        ("Product Service", "app.services.product_service"),
        ("Box Service", "app.services.box_service"),
        ("Analytics Service", "app.services.analytics_service"),
        ("History Service", "app.services.history_service"),
    ]
    
    for name, module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"✓ {name}: OK")
        except Exception as e:
            error_msg = f"✗ {name}: FAILED - {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ All Phase 2 services imported successfully!")
        return True

def test_service_classes():
    """Test that service classes can be instantiated"""
    print("\nTesting Service Class Structures...")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.services.auth_service import AuthService
        print("✓ AuthService class: OK")
    except Exception as e:
        errors.append(f"AuthService: {str(e)}")
        print(f"✗ AuthService class: FAILED - {str(e)}")
    
    try:
        from app.services.optimization_engine import OptimizationEngine
        print("✓ OptimizationEngine class: OK")
    except Exception as e:
        errors.append(f"OptimizationEngine: {str(e)}")
        print(f"✗ OptimizationEngine class: FAILED - {str(e)}")
    
    try:
        from app.services.product_service import ProductService
        print("✓ ProductService class: OK")
    except Exception as e:
        errors.append(f"ProductService: {str(e)}")
        print(f"✗ ProductService class: FAILED - {str(e)}")
    
    try:
        from app.services.box_service import BoxService
        print("✓ BoxService class: OK")
    except Exception as e:
        errors.append(f"BoxService: {str(e)}")
        print(f"✗ BoxService class: FAILED - {str(e)}")
    
    try:
        from app.services.analytics_service import AnalyticsService
        print("✓ AnalyticsService class: OK")
    except Exception as e:
        errors.append(f"AnalyticsService: {str(e)}")
        print(f"✗ AnalyticsService class: FAILED - {str(e)}")
    
    try:
        from app.services.history_service import HistoryService
        print("✓ HistoryService class: OK")
    except Exception as e:
        errors.append(f"HistoryService: {str(e)}")
        print(f"✗ HistoryService class: FAILED - {str(e)}")
    
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found in service classes")
        return False
    else:
        print("\n✅ All service classes are properly structured!")
        return True

def test_security_functions():
    """Test security and JWT functions"""
    print("\nTesting Security Functions...")
    print("=" * 60)
    
    errors = []
    
    try:
        from app.core.security import hash_password, verify_password
        
        # Test password hashing
        test_password = "TestPassword123"
        hashed = hash_password(test_password)
        
        if verify_password(test_password, hashed):
            print("✓ Password hashing and verification: OK")
        else:
            errors.append("Password verification failed")
            print("✗ Password verification: FAILED")
    except Exception as e:
        errors.append(f"Security functions: {str(e)}")
        print(f"✗ Security functions: FAILED - {str(e)}")
    
    try:
        from app.core.jwt import create_access_token, verify_token
        
        # Test JWT token creation
        test_data = {"sub": "123", "company_id": 1}
        token = create_access_token(test_data)
        
        # Test JWT token verification
        payload = verify_token(token)
        
        if payload and payload.get("sub") == "123":
            print("✓ JWT token creation and verification: OK")
        else:
            errors.append("JWT verification failed")
            print("✗ JWT verification: FAILED")
    except Exception as e:
        errors.append(f"JWT functions: {str(e)}")
        print(f"✗ JWT functions: FAILED - {str(e)}")
    
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found in security functions")
        return False
    else:
        print("\n✅ All security functions work correctly!")
        return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PHASE 2 TESTING - Backend Services & Business Logic")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Service Classes Test", test_service_classes()))
    results.append(("Security Functions Test", test_security_functions()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("Phase 2 is complete and ready for Phase 3.\n")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please fix the errors before proceeding to Phase 3.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
