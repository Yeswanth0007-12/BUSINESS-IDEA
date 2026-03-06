from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Dict, Any


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    product_id: int
    quantity: int
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    order_number: str = Field(..., min_length=1, max_length=100)
    customer_name: str = Field(..., min_length=1, max_length=200)
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Order must have at least one item")


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    order_number: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'processing', 'completed', 'failed']:
            raise ValueError('Status must be one of: pending, processing, completed, failed')
        return v


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    company_id: int
    order_number: str
    customer_name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderPackingResultResponse(BaseModel):
    """Schema for order packing result response"""
    id: int
    order_id: int
    box_id: int
    box_number: int
    products_packed: List[Dict[str, Any]]  # List of {product_id, quantity}
    total_weight: float
    space_utilization: float
    shipping_cost: float
    
    class Config:
        from_attributes = True


class OrderPackingSummary(BaseModel):
    """Schema for order packing optimization summary"""
    order_id: int
    order_number: str
    total_boxes: int
    total_cost: float
    total_shipping_cost: float
    success: bool
    packing_results: List[OrderPackingResultResponse]
    unpacked_items: List[Dict[str, Any]] = []  # Items that couldn't be packed
    message: str
