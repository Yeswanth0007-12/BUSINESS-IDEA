from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class OptimizationRequest(BaseModel):
    product_ids: Optional[List[int]] = None  # None = all products
    courier_rate: float = 2.5  # Phase 3: Courier rate per kg (default 2.5)


class OptimizationResult(BaseModel):
    product_id: int
    product_name: str
    current_box_id: int
    current_box_name: str
    current_cost: float
    recommended_box_id: int
    recommended_box_name: str
    recommended_cost: float
    savings: float
    savings_percentage: float
    volumetric_weight_current: float
    volumetric_weight_recommended: float
    # Phase 2: Advanced Packing Engine fields
    orientation: Optional[tuple[float, float, float]] = None
    space_utilization: float = 0.0
    unused_volume: float = 0.0
    # Phase 3: Shipping Cost fields
    shipping_cost_current: float = 0.0
    shipping_cost_recommended: float = 0.0
    total_cost_current: float = 0.0
    total_cost_recommended: float = 0.0
    billable_weight_current: float = 0.0
    billable_weight_recommended: float = 0.0
    # Phase 2: Advanced Packing Engine fields
    orientation: Optional[tuple[float, float, float]] = None
    space_utilization: float = 0.0
    unused_volume: float = 0.0



class OptimizationSummary(BaseModel):
    total_products_analyzed: int
    products_with_savings: int
    total_monthly_savings: float
    total_annual_savings: float
    results: List[OptimizationResult]
    run_id: int
    timestamp: datetime


class OptimizationRunResponse(BaseModel):
    id: int
    company_id: int
    timestamp: datetime
    products_analyzed: int
    total_monthly_savings: float
    total_annual_savings: float
    
    class Config:
        from_attributes = True
