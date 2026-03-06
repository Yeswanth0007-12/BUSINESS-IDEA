"""
Schemas for optimization task tracking and status.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime


class TaskSubmitResponse(BaseModel):
    """Response when submitting an asynchronous task."""
    task_id: UUID4 = Field(..., description="Unique task identifier for tracking")
    status: str = Field(default="pending", description="Initial task status")
    message: str = Field(default="Task queued successfully", description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Task queued successfully"
            }
        }


class TaskStatusResponse(BaseModel):
    """Response for task status queries."""
    task_id: UUID4 = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task (single, bulk, order)")
    status: str = Field(..., description="Current status (pending, processing, completed, failed)")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    created_at: datetime = Field(..., description="When the task was created")
    started_at: Optional[datetime] = Field(None, description="When the task started processing")
    completed_at: Optional[datetime] = Field(None, description="When the task completed or failed")
    result_id: Optional[int] = Field(None, description="ID of optimization result if completed")
    error_message: Optional[str] = Field(None, description="Error details if task failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional task information")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_type": "single",
                "status": "completed",
                "progress": 100,
                "created_at": "2024-01-15T10:00:00Z",
                "started_at": "2024-01-15T10:00:01Z",
                "completed_at": "2024-01-15T10:00:05Z",
                "result_id": 123,
                "error_message": None,
                "metadata": {"product_id": 456}
            }
        }


class TaskResultResponse(BaseModel):
    """Response for retrieving task results."""
    task_id: UUID4 = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Optimization result data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "result": {
                    "recommended_box": "Medium Box",
                    "total_monthly_savings": 150.50,
                    "space_utilization": 68.5
                }
            }
        }
