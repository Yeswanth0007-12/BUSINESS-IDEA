from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExportRequest(BaseModel):
    resource_type: str  # 'products', 'boxes', 'optimizations', 'audit_logs'
    format: str = 'csv'  # 'csv' or 'pdf'
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[dict] = None


class ExportResponse(BaseModel):
    file_url: str
    file_name: str
    expires_at: datetime
