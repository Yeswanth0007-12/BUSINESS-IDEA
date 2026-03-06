"""
Bulk Upload Schemas

Pydantic schemas for bulk CSV upload operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BulkUploadResponse(BaseModel):
    """Response schema for bulk upload record."""
    id: int
    company_id: int
    filename: str
    total_orders: int
    processed_orders: int
    failed_orders: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BulkUploadSummary(BaseModel):
    """Summary response after initiating bulk upload."""
    upload_id: int
    total_orders: int
    successful: int
    failed: int
    task_ids: List[str] = Field(default_factory=list)
    status: str
    message: str
    failed_details: List[Dict[str, Any]] = Field(default_factory=list)  # Detailed failure info


class BulkUploadOrderResponse(BaseModel):
    """Response schema for individual order within bulk upload."""
    id: int
    upload_id: int
    row_number: int
    order_data: Dict[str, Any]
    status: str
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class BulkUploadFailedOrdersResponse(BaseModel):
    """Response schema for failed orders in a bulk upload."""
    upload_id: int
    failed_count: int
    failed_orders: List[BulkUploadOrderResponse]
