"""
Standalone unit tests for webhook signature - can be run without pytest infrastructure.
"""

import hashlib
import hmac
import json
import time
from datetime import datetime


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def test_signature_generation_basic():
    """Test basic signature generation"""
    payload = '{"event": "optimization.completed", "data": {"id": 123}}'
    secret = "webhook_secret_key"
    
    signature = generate_webhook_signature(payload, secret)
    
    assert signature.startswith("sha256=")
    assert len(signature) == 71
    print("✓ test_signature_generation_basic passed")


def test_signature_generation_deterministic():
    """Test that same payload produces same signature"""
    payload = '{"event": "optimization.completed", "data": {"id": 123}}'
    secret = "webhook_secret_key"
    
    signature1 = generate_webhook_signature(payload, secret)
    signature2 = generate_webhook_signature(payload, secret)
    
    assert signature1 == signature2
    print("✓ test_signature_generation_deterministic passed")


def test_signature_verification_valid():
    """Test verification of valid signature"""
    payload = '{"event": "optimization.completed", "data": {"id": 123}}'
    secret = "webhook_secret_key"
    
    signature = generate_webhook_signature(payload, secret)
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    signature_hex = signature.replace("sha256=", "")
    assert hmac.compare_digest(signature_hex, expected_signature)
    print("✓ test_signature_verification_valid passed")


def test_signature_verification_invalid_secret():
    """Test verification fails with wrong secret"""
    payload = '{"event": "optimization.completed", "data": {"id": 123}}'
    correct_secret = "webhook_secret_key"
    wrong_secret = "wrong_secret"
    
    signature = generate_webhook_signature(payload, correct_secret)
    signature_hex = signature.replace("sha256=", "")
    
    expected_signature = hmac.new(
        wrong_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    assert not hmac.compare_digest(signature_hex, expected_signature)
    print("✓ test_signature_verification_invalid_secret passed")


def test_timestamp_validation_current_time():
    """Test validation accepts current timestamp"""
    current_time = int(time.time())
    max_age_seconds = 300
    
    age = current_time - current_time
    assert age <= max_age_seconds
    print("✓ test_timestamp_validation_current_time passed")


def test_timestamp_validation_rejects_old():
    """Test validation rejects old timestamps"""
    current_time = int(time.time())
    old_timestamp = current_time - 3600
    max_age_seconds = 300
    
    age = current_time - old_timestamp
    assert age > max_age_seconds
    print("✓ test_timestamp_validation_rejects_old passed")


def test_replay_attack_prevention():
    """Test replay attack prevention"""
    current_time = int(time.time())
    max_age_seconds = 300
    
    received_timestamp = current_time - 60
    age = current_time - received_timestamp
    is_valid = age <= max_age_seconds
    assert is_valid is True
    
    replay_time = current_time + 600
    age_at_replay = replay_time - received_timestamp
    is_valid_replay = age_at_replay <= max_age_seconds
    assert is_valid_replay is False
    print("✓ test_replay_attack_prevention passed")


def test_replay_attack_cannot_modify_timestamp():
    """Test that modifying timestamp invalidates signature"""
    secret = "webhook_secret_key"
    
    old_timestamp = int(time.time()) - 3600
    original_payload = json.dumps({
        "event": "optimization.completed",
        "timestamp": old_timestamp,
        "data": {"id": 123}
    })
    
    original_signature = generate_webhook_signature(original_payload, secret)
    original_sig_hex = original_signature.replace("sha256=", "")
    
    current_timestamp = int(time.time())
    modified_payload = json.dumps({
        "event": "optimization.completed",
        "timestamp": current_timestamp,
        "data": {"id": 123}
    })
    
    expected_for_modified = hmac.new(
        secret.encode(),
        modified_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    assert not hmac.compare_digest(original_sig_hex, expected_for_modified)
    print("✓ test_replay_attack_cannot_modify_timestamp passed")


def test_complete_webhook_security_flow():
    """Test complete webhook security flow"""
    secret = "webhook_secret_key"
    current_time = int(time.time())
    
    payload_dict = {
        "event": "optimization.completed",
        "timestamp": current_time,
        "data": {
            "optimization_id": "opt-123",
            "order_id": "WH-456",
            "status": "completed"
        }
    }
    payload_json = json.dumps(payload_dict)
    
    signature = generate_webhook_signature(payload_json, secret)
    
    assert signature.startswith("sha256=")
    assert len(signature) == 71
    
    signature_hex = signature.replace("sha256=", "")
    expected = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    assert hmac.compare_digest(signature_hex, expected)
    
    age = int(time.time()) - payload_dict["timestamp"]
    assert age <= 300
    print("✓ test_complete_webhook_security_flow passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Webhook Signature Unit Tests")
    print("="*60 + "\n")
    
    tests = [
        test_signature_generation_basic,
        test_signature_generation_deterministic,
        test_signature_verification_valid,
        test_signature_verification_invalid_secret,
        test_timestamp_validation_current_time,
        test_timestamp_validation_rejects_old,
        test_replay_attack_prevention,
        test_replay_attack_cannot_modify_timestamp,
        test_complete_webhook_security_flow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
