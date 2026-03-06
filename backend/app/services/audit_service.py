from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List
import json

from app.models.audit_log import AuditLog
from app.core.enums import AuditAction
from app.schemas.audit import AuditLogResponse, AuditLogFilterRequest


class AuditService:
    """Audit logging service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        company_id: int,
        user_id: int,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[int] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLogResponse:
        """Log an audit event."""
        audit_log = AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=json.dumps(changes) if changes else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return AuditLogResponse.model_validate(audit_log)
    
    def get_audit_logs(
        self,
        company_id: int,
        filters: Optional[AuditLogFilterRequest] = None
    ) -> List[AuditLogResponse]:
        """Get audit logs with optional filters."""
        query = self.db.query(AuditLog).filter(AuditLog.company_id == company_id)
        
        if filters:
            if filters.user_id:
                query = query.filter(AuditLog.user_id == filters.user_id)
            
            if filters.action:
                query = query.filter(AuditLog.action == filters.action)
            
            if filters.resource_type:
                query = query.filter(AuditLog.resource_type == filters.resource_type)
            
            if filters.start_date:
                query = query.filter(AuditLog.created_at >= filters.start_date)
            
            if filters.end_date:
                query = query.filter(AuditLog.created_at <= filters.end_date)
            
            limit = filters.limit
        else:
            limit = 100
        
        logs = query.order_by(desc(AuditLog.created_at)).limit(limit).all()
        
        return [AuditLogResponse.model_validate(log) for log in logs]
