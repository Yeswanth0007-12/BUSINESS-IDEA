from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.subscription_service import SubscriptionService
from app.services.usage_service import UsageService
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    CompanySubscriptionResponse,
    SubscriptionUpgradeRequest,
    SubscriptionCancelRequest
)
from app.schemas.usage import UsageSummaryResponse


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def list_subscription_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available subscription plans."""
    subscription_service = SubscriptionService(db)
    return subscription_service.list_plans()


@router.get("/current", response_model=CompanySubscriptionResponse)
def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current subscription for the company."""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_company_subscription(current_user.company_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return CompanySubscriptionResponse.model_validate(subscription)


@router.get("/usage", response_model=UsageSummaryResponse)
def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage summary for the company."""
    usage_service = UsageService(db)
    return usage_service.get_usage_summary(current_user.company_id)


@router.post("/upgrade", response_model=CompanySubscriptionResponse)
def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade the company's subscription plan."""
    subscription_service = SubscriptionService(db)
    return subscription_service.upgrade_subscription(
        company_id=current_user.company_id,
        plan_name=request.plan_name
    )


@router.post("/cancel", response_model=CompanySubscriptionResponse)
def cancel_subscription(
    request: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel the company's subscription."""
    subscription_service = SubscriptionService(db)
    return subscription_service.cancel_subscription(
        company_id=current_user.company_id,
        cancel_at_period_end=request.cancel_at_period_end
    )
