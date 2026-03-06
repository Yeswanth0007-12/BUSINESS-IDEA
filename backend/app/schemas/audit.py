from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import AuditAction


class AuditLogResponse(BaseModel):
    id: int
    company_id: int
    user_id: int
    action: AuditAction
    resource_type: str
    resource_id: Optional[int] = None
    changes: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogFilterRequest(BaseModel):
    user_id: Optional[int] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
