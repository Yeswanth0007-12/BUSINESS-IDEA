"""
Simple test runner for webhook signature tests that bypasses conftest issues.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Now run the tests manually
if __name__ == '__main__':
    import pytest
    
    # Run tests without loading conftest
    exit_code = pytest.main([
        'test_webhook_signature.py',
        '-v',
        '--tb=short',
        '-p', 'no:cacheprovider',
        '--ignore=conftest.py'
    ])
    
    sys.exit(exit_code)
