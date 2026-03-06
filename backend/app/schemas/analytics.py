from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DashboardMetrics(BaseModel):
    total_products: int
    total_boxes: int
    total_monthly_savings: float
    total_annual_savings: float
    average_savings_per_product: float
    optimization_runs_count: int
    last_optimization_date: Optional[datetime]


class LeakageInsight(BaseModel):
    category: str
    total_leakage: float
    product_count: int
    percentage_of_total: float


class InefficientProduct(BaseModel):
    product_id: int
    product_name: str
    sku: str
    current_cost: float
    potential_savings: float
    savings_percentage: float


class SavingsTrend(BaseModel):
    date: datetime
    monthly_savings: float
    annual_savings: float
