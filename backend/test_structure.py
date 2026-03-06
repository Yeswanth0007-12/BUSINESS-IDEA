"""
Test script to verify Phase 1 structure without dependencies
"""
import os
import sys

def test_structure():
    """Test that all required files and directories exist"""
    
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/models/company.py',
        'app/models/user.py',
        'app/models/product.py',
        'app/models/box.py',
        'app/models/optimization_run.py',
        'app/models/optimization_result.py',
        'requirements.txt',
        '.env.example',
        'alembic.ini',
        'alembic/env.py',
        'alembic/versions/001_initial_migration.py',
    ]
    
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/schemas',
        'app/services',
        'alembic',
        'alembic/versions',
    ]
    
    print("Testing Phase 1 Backend Structure...")
    print("=" * 50)
    
    # Test directories
    print("\n✓ Testing Directories:")
    all_dirs_exist = True
    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_path}")
        if not exists:
            all_dirs_exist = False
    
    # Test files
    print("\n✓ Testing Files:")
    all_files_exist = True
    for file_path in required_files:
        exists = os.path.isfile(file_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path}")
        if not exists:
            all_files_exist = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_dirs_exist and all_files_exist:
        print("✅ Phase 1 Backend Structure: PASSED")
        print("All required files and directories exist!")
        return True
    else:
        print("❌ Phase 1 Backend Structure: FAILED")
        print("Some files or directories are missing!")
        return False

if __name__ == "__main__":
    success = test_structure()
    sys.exit(0 if success else 1)
