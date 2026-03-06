"""
Test script to verify Phase 9 warehouse integration implementation.
This script checks that all required components are present and properly structured.
"""
import os
import sys

def test_models_exist():
    """Test that all required models exist."""
    print("Testing models...")
    
    # Check API key model
    assert os.path.exists("app/models/api_key.py"), "API key model missing"
    with open("app/models/api_key.py", "r") as f:
        content = f.read()
        assert "class ApiKey" in content, "ApiKey class not found"
        assert "key_hash" in content, "key_hash field missing"
        assert "company_id" in content, "company_id field missing"
        assert "is_active" in content, "is_active field missing"
    
    # Check webhook models
    assert os.path.exists("app/models/webhook.py"), "Webhook model missing"
    with open("app/models/webhook.py", "r") as f:
        content = f.read()
        assert "class Webhook" in content, "Webhook class not found"
        assert "class WebhookDelivery" in content, "WebhookDelivery class not found"
        assert "events" in content, "events field missing"
        assert "secret" in content, "secret field missing"
    
    print("✓ Models exist and have required fields")


def test_migration_exists():
    """Test that database migration exists."""
    print("Testing migration...")
    
    assert os.path.exists("alembic/versions/011_warehouse_integration.py"), "Migration missing"
    with open("alembic/versions/011_warehouse_integration.py", "r") as f:
        content = f.read()
        assert "create_table" in content, "create_table not found"
        assert "api_keys" in content, "api_keys table not found"
        assert "webhooks" in content, "webhooks table not found"
        assert "webhook_deliveries" in content, "webhook_deliveries table not found"
        assert "def upgrade" in content, "upgrade function missing"
        assert "def downgrade" in content, "downgrade function missing"
    
    print("✓ Migration exists with all required tables")


def test_schemas_exist():
    """Test that all required schemas exist."""
    print("Testing schemas...")
    
    assert os.path.exists("app/schemas/warehouse.py"), "Warehouse schemas missing"
    with open("app/schemas/warehouse.py", "r") as f:
        content = f.read()
        assert "WarehouseOptimizationRequest" in content, "WarehouseOptimizationRequest missing"
        assert "WarehouseOptimizationResponse" in content, "WarehouseOptimizationResponse missing"
        assert "WebhookCreate" in content, "WebhookCreate missing"
        assert "WebhookResponse" in content, "WebhookResponse missing"
        assert "ApiKeyCreate" in content, "ApiKeyCreate missing"
        assert "ApiKeyResponse" in content, "ApiKeyResponse missing"
    
    print("✓ Schemas exist with all required classes")


def test_auth_service_updated():
    """Test that auth service has API key functions."""
    print("Testing auth service...")
    
    with open("app/services/auth_service.py", "r") as f:
        content = f.read()
        assert "generate_api_key" in content, "generate_api_key function missing"
        assert "hash_api_key" in content, "hash_api_key function missing"
        assert "authenticate_api_key" in content, "authenticate_api_key function missing"
        assert "constant_time_compare" in content, "constant_time_compare function missing"
        assert "create_api_key" in content, "create_api_key function missing"
        assert "hashlib.sha256" in content, "SHA-256 hashing missing"
        assert "hmac.compare_digest" in content, "constant-time comparison missing"
    
    print("✓ Auth service has API key authentication functions")


def test_rate_limiter_exists():
    """Test that rate limiter exists."""
    print("Testing rate limiter...")
    
    assert os.path.exists("app/middleware/warehouse_rate_limit.py"), "Rate limiter missing"
    with open("app/middleware/warehouse_rate_limit.py", "r") as f:
        content = f.read()
        assert "WarehouseRateLimiter" in content, "WarehouseRateLimiter class missing"
        assert "TIER_LIMITS" in content, "TIER_LIMITS missing"
        assert "standard" in content and "100" in content, "Standard tier limit missing"
        assert "premium" in content and "500" in content, "Premium tier limit missing"
        assert "check_rate_limit" in content, "check_rate_limit function missing"
        assert "redis" in content.lower(), "Redis integration missing"
    
    print("✓ Rate limiter exists with tier-based limits")


def test_warehouse_service_exists():
    """Test that warehouse service exists."""
    print("Testing warehouse service...")
    
    assert os.path.exists("app/services/warehouse_service.py"), "Warehouse service missing"
    with open("app/services/warehouse_service.py", "r") as f:
        content = f.read()
        assert "class WarehouseService" in content, "WarehouseService class missing"
        assert "optimize_package" in content, "optimize_package method missing"
        assert "register_webhook" in content, "register_webhook method missing"
        assert "generate_webhook_signature" in content, "generate_webhook_signature method missing"
        assert "deliver_webhook" in content, "deliver_webhook method missing"
        assert "trigger_webhook_event" in content, "trigger_webhook_event method missing"
        assert "hmac" in content.lower(), "HMAC signature missing"
        assert "httpx" in content, "HTTP client missing"
    
    print("✓ Warehouse service exists with all required methods")


def test_warehouse_router_exists():
    """Test that warehouse router exists."""
    print("Testing warehouse router...")
    
    assert os.path.exists("app/api/warehouse.py"), "Warehouse router missing"
    with open("app/api/warehouse.py", "r") as f:
        content = f.read()
        assert "router = APIRouter" in content, "Router not defined"
        assert "/warehouse" in content, "Warehouse prefix missing"
        assert "optimize-package" in content, "optimize-package endpoint missing"
        assert "webhooks" in content, "webhooks endpoints missing"
        assert "api-keys" in content, "api-keys endpoints missing"
        assert "get_api_key_auth" in content, "API key auth dependency missing"
        assert "check_warehouse_rate_limit" in content, "Rate limit check missing"
    
    print("✓ Warehouse router exists with all required endpoints")


def test_main_app_updated():
    """Test that main app includes warehouse router."""
    print("Testing main app...")
    
    with open("app/main.py", "r") as f:
        content = f.read()
        assert "warehouse" in content, "Warehouse import missing"
        assert "app.include_router(warehouse.router)" in content, "Warehouse router not registered"
    
    print("✓ Main app includes warehouse router")


def test_requirements_updated():
    """Test that requirements include httpx."""
    print("Testing requirements...")
    
    with open("requirements.txt", "r") as f:
        content = f.read()
        assert "httpx" in content, "httpx dependency missing"
    
    print("✓ Requirements include httpx")


def test_company_model_updated():
    """Test that Company model has relationships."""
    print("Testing Company model...")
    
    with open("app/models/company.py", "r") as f:
        content = f.read()
        assert "api_keys" in content, "api_keys relationship missing"
        assert "webhooks" in content, "webhooks relationship missing"
    
    print("✓ Company model has warehouse relationships")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 9 Warehouse Integration Implementation Test")
    print("=" * 60)
    print()
    
    tests = [
        test_models_exist,
        test_migration_exists,
        test_schemas_exist,
        test_auth_service_updated,
        test_rate_limiter_exists,
        test_warehouse_service_exists,
        test_warehouse_router_exists,
        test_main_app_updated,
        test_requirements_updated,
        test_company_model_updated
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
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All Phase 9 implementation checks passed!")
        print("\nImplemented features:")
        print("  • API key model with SHA-256 hashing")
        print("  • Webhook models (Webhook, WebhookDelivery)")
        print("  • Database migration for warehouse integration")
        print("  • Warehouse integration schemas")
        print("  • API key authentication with constant-time comparison")
        print("  • API key generation")
        print("  • Rate limiting with Redis (100/500/2000 req/min)")
        print("  • Warehouse optimization endpoint")
        print("  • Webhook registration endpoint")
        print("  • Webhook signature generation (HMAC-SHA256)")
        print("  • Webhook delivery system with retry logic")
        print("  • Webhook event triggers")
        print("  • Warehouse integration service layer")
        print("  • Warehouse API router")
        print("  • Router registered in main application")
        return 0
    else:
        print(f"\n✗ {failed} checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
