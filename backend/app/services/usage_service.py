from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from typing import Optional
import json

from app.models.usage_record import UsageRecord
from app.models.product import Product
from app.models.box import Box
from app.models.optimization_run import OptimizationRun
from app.core.enums import UsageAction
from app.schemas.usage import UsageRecordResponse, UsageSummaryResponse
from app.services.subscription_service import SubscriptionService


class UsageService:
    """Usage tracking and monitoring service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
    
    def track_usage(
        self,
        company_id: int,
        user_id: int,
        action: UsageAction,
        resource_type: str,
        resource_id: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> UsageRecordResponse:
        """Track a usage event."""
        usage_record = UsageRecord(
            company_id=company_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            extra_data=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(usage_record)
        self.db.commit()
        self.db.refresh(usage_record)
        
        return UsageRecordResponse.model_validate(usage_record)
    
    def get_usage_summary(self, company_id: int) -> UsageSummaryResponse:
        """Get usage summary for a company."""
        # Count total resources
        total_products = self.db.query(func.count(Product.id)).filter(
            Product.company_id == company_id
        ).scalar() or 0
        
        total_boxes = self.db.query(func.count(Box.id)).filter(
            Box.company_id == company_id
        ).scalar() or 0
        
        total_optimizations = self.db.query(func.count(OptimizationRun.id)).filter(
            OptimizationRun.company_id == company_id
        ).scalar() or 0
        
        # Count optimizations this month
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        
        optimizations_this_month = self.db.query(func.count(OptimizationRun.id)).filter(
            OptimizationRun.company_id == company_id,
            extract('month', OptimizationRun.timestamp) == current_month,
            extract('year', OptimizationRun.timestamp) == current_year
        ).scalar() or 0
        
        # Get subscription limits
        try:
            limits = self.subscription_service.get_subscription_limits(company_id)
            max_optimizations = limits.get('max_optimizations_per_month', 100)
        except Exception:
            # Default to free plan limits if subscription service fails
            max_optimizations = 100
        
        # Calculate limit status
        if max_optimizations is None or max_optimizations == 0:
            # Unlimited
            limit_reached = False
            limit_percentage = 0.0
        else:
            limit_reached = optimizations_this_month >= max_optimizations
            limit_percentage = (optimizations_this_month / max_optimizations * 100)
        
        return UsageSummaryResponse(
            total_products=total_products,
            total_boxes=total_boxes,
            total_optimizations=total_optimizations,
            optimizations_this_month=optimizations_this_month,
            limit_reached=limit_reached,
            limit_percentage=min(limit_percentage, 100.0)
        )
