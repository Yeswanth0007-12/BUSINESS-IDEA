from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, List
import json

from app.models.subscription import SubscriptionPlanModel, CompanySubscription
from app.models.company import Company
from app.core.enums import SubscriptionPlan, SubscriptionStatus
from app.schemas.subscription import (
    SubscriptionPlanResponse,
    CompanySubscriptionResponse,
    SubscriptionUpgradeRequest
)


class SubscriptionService:
    """Subscription management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_company_subscription(self, company_id: int) -> Optional[CompanySubscription]:
        """Get the active subscription for a company."""
        return self.db.query(CompanySubscription).filter(
            CompanySubscription.company_id == company_id,
            CompanySubscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    def get_subscription_limits(self, company_id: int) -> dict:
        """Get subscription limits for a company."""
        subscription = self.get_company_subscription(company_id)
        
        if not subscription:
            # Return free plan limits as default
            free_plan = self.db.query(SubscriptionPlanModel).filter(
                SubscriptionPlanModel.name == SubscriptionPlan.FREE
            ).first()
            
            if free_plan:
                return {
                    'max_products': free_plan.max_products,
                    'max_boxes': free_plan.max_boxes,
                    'max_optimizations_per_month': free_plan.max_optimizations_per_month
                }
            else:
                # Default free plan limits if no plan exists in database
                return {
                    'max_products': 100,
                    'max_boxes': 50,
                    'max_optimizations_per_month': 100
                }
        
        plan = subscription.plan
        return {
            'max_products': plan.max_products,
            'max_boxes': plan.max_boxes,
            'max_optimizations_per_month': plan.max_optimizations_per_month
        }
    
    def check_limit(self, company_id: int, resource_type: str, current_count: int) -> bool:
        """Check if a company has reached its limit for a resource."""
        limits = self.get_subscription_limits(company_id)
        
        if resource_type == 'products':
            return current_count < limits['max_products']
        elif resource_type == 'boxes':
            return current_count < limits['max_boxes']
        elif resource_type == 'optimizations':
            return current_count < limits['max_optimizations_per_month']
        
        return True
    
    def require_limit(self, company_id: int, resource_type: str, current_count: int):
        """Raise exception if limit is reached."""
        if not self.check_limit(company_id, resource_type, current_count):
            limits = self.get_subscription_limits(company_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription limit reached for {resource_type}. Upgrade your plan to continue."
            )
    
    def list_plans(self) -> List[SubscriptionPlanResponse]:
        """List all available subscription plans."""
        plans = self.db.query(SubscriptionPlanModel).all()
        return [SubscriptionPlanResponse.model_validate(plan) for plan in plans]
    
    def upgrade_subscription(self, company_id: int, plan_name: SubscriptionPlan) -> CompanySubscriptionResponse:
        """Upgrade a company's subscription plan."""
        # Get the new plan
        new_plan = self.db.query(SubscriptionPlanModel).filter(
            SubscriptionPlanModel.name == plan_name
        ).first()
        
        if not new_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )
        
        # Get current subscription
        current_subscription = self.get_company_subscription(company_id)
        
        if current_subscription:
            # Update existing subscription
            current_subscription.plan_id = new_plan.id
            current_subscription.status = SubscriptionStatus.ACTIVE
            current_subscription.current_period_start = datetime.utcnow()
            current_subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            current_subscription.cancel_at_period_end = False
            current_subscription.updated_at = datetime.utcnow()
        else:
            # Create new subscription
            current_subscription = CompanySubscription(
                company_id=company_id,
                plan_id=new_plan.id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                cancel_at_period_end=False
            )
            self.db.add(current_subscription)
        
        self.db.commit()
        self.db.refresh(current_subscription)
        
        return CompanySubscriptionResponse.model_validate(current_subscription)
    
    def cancel_subscription(self, company_id: int, cancel_at_period_end: bool = True) -> CompanySubscriptionResponse:
        """Cancel a company's subscription."""
        subscription = self.get_company_subscription(company_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        if cancel_at_period_end:
            subscription.cancel_at_period_end = True
        else:
            subscription.status = SubscriptionStatus.CANCELLED
        
        subscription.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(subscription)
        
        return CompanySubscriptionResponse.model_validate(subscription)
