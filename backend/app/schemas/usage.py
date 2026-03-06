from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import UsageAction


class UsageRecordResponse(BaseModel):
    id: int
    company_id: int
    user_id: int
    action: UsageAction
    resource_type: str
    resource_id: Optional[int] = None
    extra_data: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UsageSummaryResponse(BaseModel):
    total_products: int
    total_boxes: int
    total_optimizations: int
    optimizations_this_month: int
    limit_reached: bool
    limit_percentage: float
