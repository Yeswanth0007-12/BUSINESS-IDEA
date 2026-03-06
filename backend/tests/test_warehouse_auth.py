"""
Unit tests for API key authentication and webhook signatures.
"""

import pytest
import hashlib
import hmac
import time
from app.services.warehouse_service import WarehouseService


@pytest.mark.unit
class TestAPIKeyAuthentication:
    """Test suite for API key authentication"""
    
    def setup_method(self, mock_db):
        self.service = WarehouseService(db=mock_db)
    
    def test_api_key_generation_format(self):
        """Test that API keys can be generated with proper format"""
        import secrets
        api_key = secrets.token_urlsafe(32)
        
        # Should be base64 string
        assert isinstance(api_key, str)
        assert len(api_key) > 20  # At least 32 bytes base64 encoded
        
        # Should be unique
        api_key2 = secrets.token_urlsafe(32)
        assert api_key != api_key2
    
    def test_api_key_hashing(self):
        """Test API key hashing with SHA-256"""
        api_key = "test_api_key_12345"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Hash should be 64 characters (SHA-256 hex)
        assert len(key_hash) == 64
        assert isinstance(key_hash, str)
        
        # Same key should produce same hash
        key_hash2 = hashlib.sha256(api_key.encode()).hexdigest()
        assert key_hash == key_hash2
    
    def test_api_key_verification_logic(self):
        """Test API key verification logic"""
        api_key = "test_api_key_12345"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Verify correct key
        test_hash = hashlib.sha256(api_key.encode()).hexdigest()
        assert test_hash == key_hash
        
        # Verify wrong key
        wrong_key = "wrong_api_key"
        wrong_hash = hashlib.sha256(wrong_key.encode()).hexdigest()
        assert wrong_hash != key_hash
    
    def test_constant_time_comparison_concept(self):
        """Test constant-time comparison concept using hmac.compare_digest"""
        api_key = "test_api_key_12345"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Correct key
        test_hash = hashlib.sha256(api_key.encode()).hexdigest()
        is_valid = hmac.compare_digest(test_hash, key_hash)
        assert is_valid is True
        
        # Wrong key
        wrong_key = "wrong_key"
        wrong_hash = hashlib.sha256(wrong_key.encode()).hexdigest()
        is_valid = hmac.compare_digest(wrong_hash, key_hash)
        assert is_valid is False


@pytest.mark.unit
class TestWebhookSignature:
    """Test suite for webhook signature generation and verification"""
    
    def setup_method(self, mock_db):
        self.service = WarehouseService(db=mock_db)
    
    def test_signature_generation(self):
        """Test webhook signature generation"""
        payload = '{"event": "optimization.completed", "data": {"id": 123}}'
        secret = "webhook_secret_key"
        
        signature = self.service.generate_webhook_signature(payload, secret)
        
        assert signature is not None
        assert isinstance(signature, str)
        assert signature.startswith("sha256=")
        assert len(signature) == 71  # "sha256=" (7 chars) + 64 hex chars
    
    def test_signature_consistency(self):
        """Test that same payload produces same signature"""
        payload = '{"event": "optimization.completed", "data": {"id": 123}}'
        secret = "webhook_secret_key"
        
        signature1 = self.service.generate_webhook_signature(payload, secret)
        signature2 = self.service.generate_webhook_signature(payload, secret)
        
        assert signature1 == signature2
    
    def test_signature_changes_with_payload(self):
        """Test that different payloads produce different signatures"""
        payload1 = '{"event": "optimization.completed", "data": {"id": 123}}'
        payload2 = '{"event": "optimization.completed", "data": {"id": 456}}'
        secret = "webhook_secret_key"
        
        signature1 = self.service.generate_webhook_signature(payload1, secret)
        signature2 = self.service.generate_webhook_signature(payload2, secret)
        
        assert signature1 != signature2
    
    def test_signature_changes_with_secret(self):
        """Test that different secrets produce different signatures"""
        payload = '{"event": "optimization.completed", "data": {"id": 123}}'
        secret1 = "webhook_secret_key_1"
        secret2 = "webhook_secret_key_2"
        
        signature1 = self.service.generate_webhook_signature(payload, secret1)
        signature2 = self.service.generate_webhook_signature(payload, secret2)
        
        assert signature1 != signature2
    
    def test_signature_verification_logic(self):
        """Test webhook signature verification logic"""
        payload = '{"event": "optimization.completed", "data": {"id": 123}}'
        secret = "webhook_secret_key"
        
        # Generate signature
        signature = self.service.generate_webhook_signature(payload, secret)
        
        # Verify by regenerating and comparing
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Extract hex part from "sha256=..." format
        signature_hex = signature.replace("sha256=", "")
        
        # Should match
        assert hmac.compare_digest(signature_hex, expected_signature)
    
    def test_signature_verification_fails_wrong_secret(self):
        """Test signature verification fails with wrong secret"""
        payload = '{"event": "optimization.completed", "data": {"id": 123}}'
        secret = "webhook_secret_key"
        wrong_secret = "wrong_secret"
        
        # Generate with correct secret
        signature = self.service.generate_webhook_signature(payload, secret)
        signature_hex = signature.replace("sha256=", "")
        
        # Try to verify with wrong secret
        expected_signature = hmac.new(
            wrong_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Should not match
        assert not hmac.compare_digest(signature_hex, expected_signature)
    
    def test_hmac_sha256_format(self):
        """Test HMAC-SHA256 signature format"""
        payload = '{"test": "data"}'
        secret = "secret_key"
        
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Should be 64 character hex string
        assert len(signature) == 64
        assert all(c in '0123456789abcdef' for c in signature)
    
    def test_replay_attack_prevention_concept(self):
        """Test replay attack prevention using timestamps"""
        import time
        
        current_time = int(time.time())
        old_time = current_time - 3600  # 1 hour ago
        
        # Timestamp validation logic
        max_age = 300  # 5 minutes
        
        # Current timestamp should be valid
        age = current_time - current_time
        assert age <= max_age
        
        # Old timestamp should be invalid
        age = current_time - old_time
        assert age > max_age
    
    def test_timestamp_in_payload(self):
        """Test including timestamp in webhook payload"""
        import json
        import time
        
        payload_dict = {
            "event": "optimization.completed",
            "data": {"id": 123},
            "timestamp": int(time.time())
        }
        
        payload_json = json.dumps(payload_dict)
        secret = "webhook_secret_key"
        
        # Generate signature with timestamp
        signature = hmac.new(
            secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Signature should be valid
        assert len(signature) == 64
        
        # Modifying timestamp should invalidate signature
        payload_dict['timestamp'] = int(time.time()) + 1
        modified_payload = json.dumps(payload_dict)
        
        expected_signature = hmac.new(
            secret.encode(),
            modified_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Signatures should differ
        assert signature != expected_signature


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
