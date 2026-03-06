"""
Test configuration and fixtures for PackOptima test suite.

This module configures:
- Hypothesis property-based testing settings
- Pytest fixtures for database, authentication, and test data
- Test database setup and teardown
"""

import os
import sys
import pytest
from hypothesis import settings, Verbosity, HealthCheck

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Hypothesis Configuration
# Configure Hypothesis for comprehensive property-based testing
settings.register_profile(
    "default",
    max_examples=100,  # Number of test cases to generate per property
    deadline=5000,  # 5 second timeout per test case
    suppress_health_check=[
        HealthCheck.too_slow,  # Allow slower tests for complex algorithms
        HealthCheck.data_too_large,  # Allow large test data generation
    ],
    verbosity=Verbosity.normal,
)

settings.register_profile(
    "ci",
    max_examples=200,  # More examples in CI for thorough testing
    deadline=10000,  # 10 second timeout in CI
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
    ],
    verbosity=Verbosity.verbose,
)

settings.register_profile(
    "dev",
    max_examples=10,  # Fewer examples for faster local development
    deadline=2000,  # 2 second timeout for quick feedback
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
    ],
    verbosity=Verbosity.normal,
)

# Load profile from environment variable, default to "default"
profile = os.getenv("HYPOTHESIS_PROFILE", "default")
settings.load_profile(profile)


# Pytest Configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance benchmark"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security validation test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )


# Database Fixtures
from unittest.mock import MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Provide a mock database session for unit tests."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def db_session(mock_db):
    """Alias for mock_db for compatibility."""
    return mock_db
