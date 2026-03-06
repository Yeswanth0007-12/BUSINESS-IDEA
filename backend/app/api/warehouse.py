"""
Warehouse integration API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.services.warehouse_service import WarehouseService
from app.services.auth_service import authenticate_api_key, create_api_key, get_current_user
from app.models.api_key import ApiKey
from app.models.company import Company
from app.models.user import User
from app.schemas.warehouse import (
    WarehouseOptimizationRequest,
    WarehouseOptimizationResponse,
    WebhookCreate,
    WebhookResponse,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyInfo
)
from app.middleware.warehouse_rate_limit import check_warehouse_rate_limit

router = APIRouter(prefix="/api/v1/warehouse", tags=["warehouse"])


# API Key Authentication Dependency
async def get_api_key_auth(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> ApiKey:
    """
    Authenticate request using API key from Authorization header.
    
    Expected format: Authorization: Bearer <api_key>
    
    Returns:
        ApiKey object if valid
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract API key from Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <api_key>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    api_key = parts[1]
    
    # Authenticate API key
    api_key_obj = authenticate_api_key(db, api_key)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return api_key_obj


# Get subscription tier for rate limiting
def get_subscription_tier(api_key: ApiKey, db: Session) -> str:
    """
    Get subscription tier for rate limiting.
    
    Args:
        api_key: Authenticated API key
        db: Database session
        
    Returns:
        Subscription tier (standard, premium, enterprise)
    """
    # Query company subscription
    from app.models.subscription import CompanySubscription
    
    subscription = db.query(CompanySubscription).filter(
        CompanySubscription.company_id == api_key.company_id
    ).first()
    
    if subscription:
        return subscription.tier.lower()
    
    return "standard"


# Warehouse Optimization Endpoint
@router.post("/optimize-package", response_model=WarehouseOptimizationResponse)
async def optimize_package(
    request: Request,
    optimization_request: WarehouseOptimizationRequest,
    api_key: ApiKey = Depends(get_api_key_auth),
    db: Session = Depends(get_db)
):
    """
    Optimize packaging for a warehouse order.
    
    This endpoint accepts an order with multiple items and returns the optimal
    packing configuration with boxes, costs, and shipping estimates.
    
    **Authentication:** Requires API key in Authorization header
    
    **Rate Limits:**
    - Standard tier: 100 requests/minute
    - Premium tier: 500 requests/minute
    - Enterprise tier: 2000 requests/minute
    
    **Response Time Target:** < 500ms at p95
    """
    # Get subscription tier for rate limiting
    tier = get_subscription_tier(api_key, db)
    
    # Check rate limit
    await check_warehouse_rate_limit(request, api_key.id, tier)
    
    # Process optimization
    warehouse_service = WarehouseService(db)
    result = warehouse_service.optimize_package(
        api_key.company_id,
        optimization_request
    )
    
    # Trigger webhook event (async, don't wait)
    try:
        import asyncio
        asyncio.create_task(
            warehouse_service.trigger_webhook_event(
                api_key.company_id,
                "optimization.completed",
                {
                    "optimization_id": result.optimization_id,
                    "order_id": result.order_id,
                    "status": result.status,
                    "total_boxes": result.total_boxes,
                    "total_cost": result.total_cost
                }
            )
        )
    except Exception as e:
        # Don't fail the request if webhook fails
        pass
    
    return result


# Webhook Management Endpoints
@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a webhook for event notifications.
    
    **Supported Events:**
    - `optimization.completed`: Triggered when optimization succeeds
    - `optimization.failed`: Triggered when optimization fails
    
    **Webhook Payload:**
    Webhooks receive a POST request with:
    - `X-PackOptima-Signature` header with HMAC-SHA256 signature
    - `X-PackOptima-Event` header with event type
    - JSON payload with event data
    
    **Security:**
    - Webhook URL must use HTTPS
    - Payload is signed with HMAC-SHA256 using your secret
    - Verify signature to ensure authenticity
    
    **Retry Logic:**
    - Failed deliveries are retried up to 3 times
    - Exponential backoff between retries (1s, 2s, 4s)
    - Webhook deactivated after 10 consecutive failures
    
    **Authentication:** Requires JWT token (user authentication)
    """
    warehouse_service = WarehouseService(db)
    webhook = warehouse_service.register_webhook(current_user.company_id, webhook_data)
    
    return WebhookResponse(
        id=webhook.id,
        company_id=webhook.company_id,
        url=webhook.url,
        events=webhook.events,
        is_active=webhook.is_active,
        created_at=webhook.created_at
    )


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all webhooks for the authenticated company.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    warehouse_service = WarehouseService(db)
    webhooks = warehouse_service.list_webhooks(current_user.company_id)
    
    return [
        WebhookResponse(
            id=wh.id,
            company_id=wh.company_id,
            url=wh.url,
            events=wh.events,
            is_active=wh.is_active,
            created_at=wh.created_at
        )
        for wh in webhooks
    ]


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific webhook.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    warehouse_service = WarehouseService(db)
    webhook = warehouse_service.get_webhook(current_user.company_id, webhook_id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    return WebhookResponse(
        id=webhook.id,
        company_id=webhook.company_id,
        url=webhook.url,
        events=webhook.events,
        is_active=webhook.is_active,
        created_at=webhook.created_at
    )


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a webhook.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    warehouse_service = WarehouseService(db)
    deleted = warehouse_service.delete_webhook(current_user.company_id, webhook_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook {webhook_id} not found"
        )
    
    return None


# API Key Management Endpoints (for authenticated users, not API key auth)


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_new_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for warehouse integration.
    
    **Important:** The API key is only shown once at creation. Store it securely.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    api_key_obj, plaintext_key = create_api_key(
        db,
        current_user.company_id,
        key_data.name
    )
    
    return ApiKeyResponse(
        id=api_key_obj.id,
        name=api_key_obj.name,
        api_key=plaintext_key,
        created_at=api_key_obj.created_at
    )


@router.get("/api-keys", response_model=List[ApiKeyInfo])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the authenticated user's company.
    
    **Note:** The actual API key values are not returned for security.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    api_keys = db.query(ApiKey).filter(
        ApiKey.company_id == current_user.company_id
    ).all()
    
    return [
        ApiKeyInfo(
            id=key.id,
            name=key.name,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            is_active=key.is_active
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an API key.
    
    **Authentication:** Requires JWT token (user authentication)
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.company_id == current_user.company_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {key_id} not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return None
