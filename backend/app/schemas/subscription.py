from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.core.enums import SubscriptionPlan, SubscriptionStatus


class SubscriptionPlanResponse(BaseModel):
    id: int
    name: SubscriptionPlan
    price_monthly: float
    max_products: Optional[int] = None
    max_boxes: Optional[int] = None
    max_optimizations_per_month: Optional[int] = None
    features: str  # JSON string
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanySubscriptionResponse(BaseModel):
    id: int
    company_id: int
    plan_id: int
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime
    plan: Optional[SubscriptionPlanResponse] = None
    
    class Config:
        from_attributes = True


class SubscriptionUpgradeRequest(BaseModel):
    plan_name: SubscriptionPlan


class SubscriptionCancelRequest(BaseModel):
    cancel_at_period_end: bool = True
