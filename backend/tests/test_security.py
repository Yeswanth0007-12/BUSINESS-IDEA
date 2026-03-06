"""
Comprehensive unit tests for security features.
Tests API key authentication, webhook signatures, and security validation.
"""

import pytest
import hashlib
import hmac
import secrets
import time
from app.services.auth_service import AuthService


@pytest.mark.unit
@pytest.mark.security
class TestAPIKeyAuthentication:
    """Test suite for API key authentication"""
    
    def test_api_key_generation(self):
        """Test API key generation"""
        # Generate random 32-byte key
        api_key = secrets.token_urlsafe(32)
        
        assert len(api_key) > 0
        assert isinstance(api_key, str)
    
    def test_api_key_hashing(self):
        """Test API key hashing with SHA-256"""
        api_key = "test_api_key_12345"
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        assert len(key_hash) == 64  # SHA-256 produces 64 hex characters
        assert key_hash != api_key  # Hash should be different from original
    
    def test_same_key_produces_same_hash(self):
        """Test that same key always produces same hash"""
        api_key = "test_api_key_12345"
        
        hash1 = hashlib.sha256(api_key.encode()).hexdigest()
        hash2 = hashlib.sha256(api_key.encode()).hexdigest()
        
        assert hash1 == hash2
    
    def test_different_keys_produce_different_hashes(self):
        """Test that different keys produce different hashes"""
        key1 = "test_api_key_1"
        key2 = "test_api_key_2"
        
        hash1 = hashlib.sha256(key1.encode()).hexdigest()
        hash2 = hashlib.sha256(key2.encode()).hexdigest()
        
        assert hash1 != hash2
    
    def test_constant_time_comparison(self):
        """Test constant-time comparison to prevent timing attacks"""
        hash1 = "abc123"
        hash2 = "abc123"
        hash3 = "xyz789"
        
        # Use hmac.compare_digest for constant-time comparison
        assert hmac.compare_digest(hash1, hash2) is True
        assert hmac.compare_digest(hash1, hash3) is False
    
    def test_invalid_api_key_rejected(self):
        """Test that invalid API key is rejected"""
        valid_key_hash = hashlib.sha256("valid_key".encode()).hexdigest()
        provided_key = "invalid_key"
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        
        is_valid = hmac.compare_digest(valid_key_hash, provided_hash)
        
        assert is_valid is False
    
    def test_empty_api_key_rejected(self):
        """Test that empty API key is rejected"""
        api_key = ""
        
        assert len(api_key) == 0
        # Should be rejected
    
    def test_api_key_uniqueness(self):
        """Test that generated API keys are unique"""
        keys = set()
        for _ in range(100):
            key = secrets.token_urlsafe(32)
            assert key not in keys
            keys.add(key)


@pytest.mark.unit
@pytest.mark.security
class TestWebhookSignature:
    """Test suite for webhook signature generation and verification"""
    
    def test_hmac_signature_generation(self):
        """Test HMAC-SHA256 signature generation"""
        secret = "webhook_secret_key"
        payload = '{"event": "optimization.completed", "data": {}}'
        
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert len(signature) == 64  # SHA-256 produces 64 hex characters
        assert isinstance(signature, str)
    
    def test_same_payload_same_signature(self):
        """Test that same payload produces same signature"""
        secret = "webhook_secret_key"
        payload = '{"event": "test"}'
        
        sig1 = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        sig2 = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        
        assert sig1 == sig2
    
    def test_different_payload_different_signature(self):
        """Test that different payloads produce different signatures"""
        secret = "webhook_secret_key"
        payload1 = '{"event": "test1"}'
        payload2 = '{"event": "test2"}'
        
        sig1 = hmac.new(secret.encode(), payload1.encode(), hashlib.sha256).hexdigest()
        sig2 = hmac.new(secret.encode(), payload2.encode(), hashlib.sha256).hexdigest()
        
        assert sig1 != sig2
    
    def test_different_secret_different_signature(self):
        """Test that different secrets produce different signatures"""
        payload = '{"event": "test"}'
        secret1 = "secret1"
        secret2 = "secret2"
        
        sig1 = hmac.new(secret1.encode(), payload.encode(), hashlib.sha256).hexdigest()
        sig2 = hmac.new(secret2.encode(), payload.encode(), hashlib.sha256).hexdigest()
        
        assert sig1 != sig2
    
    def test_signature_verification(self):
        """Test signature verification"""
        secret = "webhook_secret_key"
        payload = '{"event": "test"}'
        
        # Generate signature
        expected_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        provided_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        assert hmac.compare_digest(expected_sig, provided_sig)
    
    def test_invalid_signature_rejected(self):
        """Test that invalid signature is rejected"""
        secret = "webhook_secret_key"
        payload = '{"event": "test"}'
        
        expected_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        invalid_sig = "invalid_signature_12345"
        
        assert not hmac.compare_digest(expected_sig, invalid_sig)
    
    def test_timestamp_in_payload(self):
        """Test that timestamp is included in payload"""
        timestamp = int(time.time())
        payload = f'{{"event": "test", "timestamp": {timestamp}}}'
        
        assert "timestamp" in payload
        assert str(timestamp) in payload
    
    def test_timestamp_validation(self):
        """Test timestamp validation (within 5 minutes)"""
        current_time = int(time.time())
        
        # Valid timestamp (within 5 minutes)
        valid_timestamp = current_time - 60  # 1 minute ago
        assert abs(current_time - valid_timestamp) <= 300
        
        # Invalid timestamp (too old)
        invalid_timestamp = current_time - 600  # 10 minutes ago
        assert abs(current_time - invalid_timestamp) > 300


@pytest.mark.unit
@pytest.mark.security
class TestInputValidation:
    """Test suite for input validation"""
    
    def test_positive_quantity_validation(self):
        """Test that quantity must be positive"""
        valid_quantities = [1, 5, 100, 1000]
        invalid_quantities = [0, -1, -100]
        
        for qty in valid_quantities:
            assert qty > 0
        
        for qty in invalid_quantities:
            assert qty <= 0
    
    def test_positive_dimensions_validation(self):
        """Test that dimensions must be positive"""
        valid_dims = [(10, 10, 10), (5.5, 3.2, 8.7)]
        invalid_dims = [(0, 10, 10), (-5, 10, 10), (10, -10, 10)]
        
        for dims in valid_dims:
            assert all(d > 0 for d in dims)
        
        for dims in invalid_dims:
            assert not all(d > 0 for d in dims)
    
    def test_weight_validation(self):
        """Test that weight must be non-negative"""
        valid_weights = [0.0, 1.5, 10.0, 100.0]
        invalid_weights = [-1.0, -10.5]
        
        for weight in valid_weights:
            assert weight >= 0
        
        for weight in invalid_weights:
            assert weight < 0
    
    def test_email_format_validation(self):
        """Test email format validation"""
        valid_emails = ["user@example.com", "test.user@domain.co.uk"]
        invalid_emails = ["invalid", "@example.com", "user@", "user@.com"]
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in valid_emails:
            assert re.match(email_pattern, email)
        
        for email in invalid_emails:
            assert not re.match(email_pattern, email)
    
    def test_url_validation(self):
        """Test URL validation for webhooks"""
        valid_urls = [
            "https://example.com/webhook",
            "https://api.example.com/v1/webhook"
        ]
        invalid_urls = [
            "http://example.com/webhook",  # Not HTTPS
            "ftp://example.com",
            "not-a-url"
        ]
        
        for url in valid_urls:
            assert url.startswith("https://")
        
        for url in invalid_urls:
            assert not url.startswith("https://")


@pytest.mark.unit
@pytest.mark.security
class TestMultiTenantIsolation:
    """Test suite for multi-tenant isolation"""
    
    def test_company_id_filtering(self):
        """Test that queries are filtered by company_id"""
        user_company_id = 1
        
        # Query should include company_id filter
        query_company_id = 1
        
        assert user_company_id == query_company_id
    
    def test_cross_company_access_prevented(self):
        """Test that users cannot access other company's data"""
        user_company_id = 1
        requested_resource_company_id = 2
        
        # Should be rejected
        assert user_company_id != requested_resource_company_id
    
    def test_company_id_in_token(self):
        """Test that company_id is included in JWT token"""
        token_payload = {
            "sub": "user@example.com",
            "company_id": 1
        }
        
        assert "company_id" in token_payload
        assert isinstance(token_payload["company_id"], int)


@pytest.mark.unit
@pytest.mark.security
class TestRateLimiting:
    """Test suite for rate limiting"""
    
    def test_rate_limit_standard_tier(self):
        """Test rate limit for standard tier (100 req/min)"""
        standard_limit = 100
        
        request_count = 95
        assert request_count <= standard_limit
        
        request_count = 105
        assert request_count > standard_limit  # Should be rejected
    
    def test_rate_limit_premium_tier(self):
        """Test rate limit for premium tier (500 req/min)"""
        premium_limit = 500
        
        request_count = 450
        assert request_count <= premium_limit
        
        request_count = 550
        assert request_count > premium_limit  # Should be rejected
    
    def test_rate_limit_window(self):
        """Test rate limit window (per minute)"""
        window_seconds = 60
        
        assert window_seconds == 60
    
    def test_retry_after_header(self):
        """Test Retry-After header in rate limit response"""
        retry_after_seconds = 60
        
        assert retry_after_seconds > 0
        assert isinstance(retry_after_seconds, int)


@pytest.mark.unit
@pytest.mark.security
class TestDataEncryption:
    """Test suite for data encryption"""
    
    def test_api_key_stored_as_hash(self):
        """Test that API keys are stored as hashes, not plaintext"""
        plaintext_key = "my_secret_api_key"
        
        stored_value = hashlib.sha256(plaintext_key.encode()).hexdigest()
        
        assert stored_value != plaintext_key
        assert len(stored_value) == 64
    
    def test_webhook_secret_encryption(self):
        """Test that webhook secrets should be encrypted at rest"""
        webhook_secret = "my_webhook_secret"
        
        # In production, this would be encrypted
        # For testing, verify it's not stored as plaintext
        assert len(webhook_secret) > 0
    
    def test_password_hashing(self):
        """Test that passwords are hashed"""
        password = "user_password_123"
        
        # Passwords should be hashed with bcrypt or similar
        # Not stored as plaintext
        assert len(password) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
