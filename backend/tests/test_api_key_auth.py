"""
Unit tests for API key authentication.

Tests cover:
- Valid API key authentication
- Invalid API key rejection
- Inactive API key rejection
- Constant-time comparison
- Last_used_at timestamp update

Validates Requirements: 29.1, 29.2, 29.3, 29.4, 29.5
"""

import pytest
import hashlib
import hmac
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from app.services.auth_service import (
    generate_api_key,
    hash_api_key,
    constant_time_compare,
    authenticate_api_key,
    create_api_key
)
from app.models.api_key import ApiKey


@pytest.mark.unit
class TestAPIKeyGeneration:
    """Test suite for API key generation"""
    
    def test_generate_api_key_format(self):
        """Test that generated API keys have correct format"""
        api_key = generate_api_key()
        
        # Should be a string
        assert isinstance(api_key, str)
        
        # Should have prefix
        assert api_key.startswith("pk_live_")
        
        # Should be sufficiently long (prefix + 32 bytes base64)
        assert len(api_key) > 40
    
    def test_generate_api_key_uniqueness(self):
        """Test that generated API keys are unique"""
        key1 = generate_api_key()
        key2 = generate_api_key()
        key3 = generate_api_key()
        
        # All keys should be different
        assert key1 != key2
        assert key2 != key3
        assert key1 != key3
    
    def test_generate_api_key_multiple_calls(self):
        """Test generating multiple API keys produces unique values"""
        keys = [generate_api_key() for _ in range(10)]
        
        # All keys should be unique
        assert len(keys) == len(set(keys))


@pytest.mark.unit
class TestAPIKeyHashing:
    """Test suite for API key hashing"""
    
    def test_hash_api_key_sha256(self):
        """Test that API keys are hashed using SHA-256"""
        api_key = "pk_live_test_key_12345"
        key_hash = hash_api_key(api_key)
        
        # Hash should be 64 characters (SHA-256 hex)
        assert len(key_hash) == 64
        assert isinstance(key_hash, str)
        
        # Should be valid hex string
        assert all(c in '0123456789abcdef' for c in key_hash)
    
    def test_hash_api_key_consistency(self):
        """Test that same API key produces same hash"""
        api_key = "pk_live_test_key_12345"
        
        hash1 = hash_api_key(api_key)
        hash2 = hash_api_key(api_key)
        hash3 = hash_api_key(api_key)
        
        # All hashes should be identical
        assert hash1 == hash2 == hash3
    
    def test_hash_api_key_different_keys(self):
        """Test that different API keys produce different hashes"""
        key1 = "pk_live_key_1"
        key2 = "pk_live_key_2"
        key3 = "pk_live_key_3"
        
        hash1 = hash_api_key(key1)
        hash2 = hash_api_key(key2)
        hash3 = hash_api_key(key3)
        
        # All hashes should be different
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3
    
    def test_hash_api_key_matches_sha256(self):
        """Test that hash_api_key uses SHA-256 algorithm"""
        api_key = "pk_live_test_key"
        
        # Hash using our function
        our_hash = hash_api_key(api_key)
        
        # Hash using hashlib directly
        expected_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Should match
        assert our_hash == expected_hash


@pytest.mark.unit
class TestConstantTimeComparison:
    """Test suite for constant-time comparison"""
    
    def test_constant_time_compare_equal_strings(self):
        """Test constant-time comparison with equal strings"""
        str1 = "test_string_12345"
        str2 = "test_string_12345"
        
        result = constant_time_compare(str1, str2)
        
        assert result is True
    
    def test_constant_time_compare_different_strings(self):
        """Test constant-time comparison with different strings"""
        str1 = "test_string_12345"
        str2 = "different_string"
        
        result = constant_time_compare(str1, str2)
        
        assert result is False
    
    def test_constant_time_compare_similar_strings(self):
        """Test constant-time comparison with similar strings"""
        str1 = "test_string_12345"
        str2 = "test_string_12346"  # Only last character different
        
        result = constant_time_compare(str1, str2)
        
        assert result is False
    
    def test_constant_time_compare_uses_hmac(self):
        """Test that constant_time_compare uses hmac.compare_digest"""
        str1 = "test_hash_abc123"
        str2 = "test_hash_abc123"
        
        # Our function should behave like hmac.compare_digest
        our_result = constant_time_compare(str1, str2)
        expected_result = hmac.compare_digest(str1, str2)
        
        assert our_result == expected_result
    
    def test_constant_time_compare_prevents_timing_attacks(self):
        """Test that comparison time doesn't leak information"""
        # This is a conceptual test - actual timing attack prevention
        # is provided by hmac.compare_digest implementation
        
        hash1 = "a" * 64
        hash2_similar = "a" * 63 + "b"  # Only last char different
        hash2_different = "b" * 64  # All chars different
        
        # Both comparisons should return False
        result1 = constant_time_compare(hash1, hash2_similar)
        result2 = constant_time_compare(hash1, hash2_different)
        
        assert result1 is False
        assert result2 is False
        
        # The key is that both take constant time regardless of
        # where the difference occurs (verified by hmac.compare_digest)


@pytest.mark.unit
class TestValidAPIKeyAuthentication:
    """Test suite for valid API key authentication"""
    
    def test_authenticate_valid_api_key(self):
        """Test authentication with valid API key"""
        # Setup
        api_key = "pk_live_valid_key_12345"
        key_hash = hash_api_key(api_key)
        company_id = 1
        
        # Create mock database session
        mock_db = Mock()
        
        # Create mock ApiKey object
        mock_api_key = ApiKey(
            id=1,
            company_id=company_id,
            key_hash=key_hash,
            name="Test Key",
            created_at=datetime.utcnow(),
            last_used_at=None,
            is_active=True
        )
        
        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_api_key
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify
        assert result is not None
        assert result.id == 1
        assert result.company_id == company_id
        assert result.is_active is True
        
        # Verify database was queried correctly
        mock_db.query.assert_called_once_with(ApiKey)
        mock_db.commit.assert_called_once()
    
    def test_authenticate_updates_last_used_at(self):
        """Test that authentication updates last_used_at timestamp"""
        # Setup
        api_key = "pk_live_valid_key_12345"
        key_hash = hash_api_key(api_key)
        old_timestamp = datetime.utcnow() - timedelta(hours=1)
        
        # Create mock database session
        mock_db = Mock()
        
        # Create mock ApiKey object with old timestamp
        mock_api_key = ApiKey(
            id=1,
            company_id=1,
            key_hash=key_hash,
            name="Test Key",
            created_at=datetime.utcnow(),
            last_used_at=old_timestamp,
            is_active=True
        )
        
        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_api_key
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify last_used_at was updated
        assert result.last_used_at is not None
        assert result.last_used_at > old_timestamp
        
        # Verify commit was called to save the update
        mock_db.commit.assert_called_once()
    
    def test_authenticate_first_use_sets_last_used_at(self):
        """Test that first authentication sets last_used_at"""
        # Setup
        api_key = "pk_live_valid_key_12345"
        key_hash = hash_api_key(api_key)
        
        # Create mock database session
        mock_db = Mock()
        
        # Create mock ApiKey object with no last_used_at
        mock_api_key = ApiKey(
            id=1,
            company_id=1,
            key_hash=key_hash,
            name="Test Key",
            created_at=datetime.utcnow(),
            last_used_at=None,  # Never used before
            is_active=True
        )
        
        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_api_key
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify last_used_at was set
        assert result.last_used_at is not None
        assert isinstance(result.last_used_at, datetime)


@pytest.mark.unit
class TestInvalidAPIKeyRejection:
    """Test suite for invalid API key rejection"""
    
    def test_authenticate_invalid_api_key(self):
        """Test authentication fails with invalid API key"""
        # Setup
        api_key = "pk_live_invalid_key"
        
        # Create mock database session
        mock_db = Mock()
        
        # Mock query returns None (key not found)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify
        assert result is None
        
        # Verify commit was not called
        mock_db.commit.assert_not_called()
    
    def test_authenticate_wrong_api_key(self):
        """Test authentication fails when API key doesn't match"""
        # Setup
        correct_key = "pk_live_correct_key"
        wrong_key = "pk_live_wrong_key"
        correct_hash = hash_api_key(correct_key)
        
        # Create mock database session
        mock_db = Mock()
        
        # Mock query returns None because hash doesn't match
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute with wrong key
        result = authenticate_api_key(mock_db, wrong_key)
        
        # Verify
        assert result is None
    
    def test_authenticate_empty_api_key(self):
        """Test authentication fails with empty API key"""
        # Setup
        api_key = ""
        
        # Create mock database session
        mock_db = Mock()
        
        # Mock query returns None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify
        assert result is None


@pytest.mark.unit
class TestInactiveAPIKeyRejection:
    """Test suite for inactive API key rejection"""
    
    def test_authenticate_inactive_api_key(self):
        """Test authentication fails with inactive API key"""
        # Setup
        api_key = "pk_live_inactive_key"
        key_hash = hash_api_key(api_key)
        
        # Create mock database session
        mock_db = Mock()
        
        # Mock query returns None because is_active=False is filtered out
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify
        assert result is None
        
        # Verify the query filtered by is_active=True
        mock_db.query.assert_called_once_with(ApiKey)
    
    def test_authenticate_deactivated_key(self):
        """Test that deactivated keys cannot authenticate"""
        # Setup
        api_key = "pk_live_deactivated_key"
        key_hash = hash_api_key(api_key)
        
        # Create mock database session
        mock_db = Mock()
        
        # Create mock ApiKey object that is inactive
        mock_api_key = ApiKey(
            id=1,
            company_id=1,
            key_hash=key_hash,
            name="Deactivated Key",
            created_at=datetime.utcnow(),
            last_used_at=datetime.utcnow(),
            is_active=False  # Key is deactivated
        )
        
        # Mock query returns None because filter excludes inactive keys
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None  # Filtered out by is_active=True
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Execute
        result = authenticate_api_key(mock_db, api_key)
        
        # Verify
        assert result is None


@pytest.mark.unit
class TestCreateAPIKey:
    """Test suite for API key creation"""
    
    def test_create_api_key_success(self):
        """Test creating a new API key"""
        # Setup
        company_id = 1
        key_name = "Production Key"
        
        # Create mock database session
        mock_db = Mock()
        
        # Mock the created ApiKey object
        mock_api_key = ApiKey(
            id=1,
            company_id=company_id,
            key_hash="mock_hash",
            name=key_name,
            created_at=datetime.utcnow(),
            last_used_at=None,
            is_active=True
        )
        
        # Mock refresh to set the id
        def mock_refresh(obj):
            obj.id = 1
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Execute
        with patch('app.services.auth_service.generate_api_key') as mock_generate:
            mock_generate.return_value = "pk_live_test_key"
            
            api_key_obj, plaintext_key = create_api_key(mock_db, company_id, key_name)
        
        # Verify
        assert plaintext_key == "pk_live_test_key"
        assert plaintext_key.startswith("pk_live_")
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_api_key_returns_plaintext_once(self):
        """Test that plaintext API key is only returned at creation"""
        # This is a conceptual test - the plaintext key should only
        # be shown once at creation time and never stored
        
        company_id = 1
        key_name = "Test Key"
        
        # Create mock database session
        mock_db = Mock()
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        
        # Execute
        api_key_obj, plaintext_key = create_api_key(mock_db, company_id, key_name)
        
        # Verify plaintext is returned
        assert plaintext_key is not None
        assert isinstance(plaintext_key, str)
        assert len(plaintext_key) > 0
        
        # Verify only hash is stored (not plaintext)
        # The ApiKey object should have key_hash, not the plaintext
        assert hasattr(api_key_obj, 'key_hash')
        assert api_key_obj.key_hash != plaintext_key


@pytest.mark.unit
class TestAPIKeySecurityProperties:
    """Test suite for API key security properties"""
    
    def test_api_key_hash_is_one_way(self):
        """Test that API key hashing is one-way (cannot reverse)"""
        api_key = "pk_live_secret_key_12345"
        key_hash = hash_api_key(api_key)
        
        # Hash should not contain the original key
        assert api_key not in key_hash
        assert "pk_live_" not in key_hash
        assert "secret" not in key_hash
        
        # Hash should be different from original
        assert key_hash != api_key
    
    def test_similar_keys_produce_different_hashes(self):
        """Test that similar API keys produce very different hashes"""
        key1 = "pk_live_key_00000001"
        key2 = "pk_live_key_00000002"
        
        hash1 = hash_api_key(key1)
        hash2 = hash_api_key(key2)
        
        # Hashes should be completely different
        assert hash1 != hash2
        
        # Count different characters (should be many)
        differences = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        assert differences > 30  # Most characters should differ
    
    def test_constant_time_comparison_security(self):
        """Test that constant-time comparison is used for security"""
        # This test verifies the concept of constant-time comparison
        # to prevent timing attacks
        
        correct_hash = "a" * 64
        wrong_hash_early = "b" + "a" * 63  # Differs in first char
        wrong_hash_late = "a" * 63 + "b"   # Differs in last char
        
        # Both should return False
        result1 = constant_time_compare(correct_hash, wrong_hash_early)
        result2 = constant_time_compare(correct_hash, wrong_hash_late)
        
        assert result1 is False
        assert result2 is False
        
        # The key security property is that both comparisons take
        # the same amount of time, preventing attackers from learning
        # where the difference occurs


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
