from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.audit_service import AuditService
from app.services.snapshot_service import SnapshotService
from app.models.user import User
from app.schemas.audit import AuditLogResponse, AuditLogFilterRequest
from app.middleware.rbac_middleware import require_admin


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filters.
    
    Requires: Admin role
    """
    audit_service = AuditService(db)
    
    filters = AuditLogFilterRequest(
        user_id=user_id,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return audit_service.get_audit_logs(current_user.company_id, filters)


@router.post("/snapshots/generate")
def generate_monthly_snapshot(
    year: int,
    month: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Generate a monthly snapshot for the company.
    
    Requires: Admin role
    """
    snapshot_service = SnapshotService(db)
    snapshot = snapshot_service.generate_monthly_snapshot(
        current_user.company_id,
        year,
        month
    )
    
    return {
        "id": snapshot.id,
        "year": snapshot.year,
        "month": snapshot.month,
        "total_products": snapshot.total_products,
        "total_boxes": snapshot.total_boxes,
        "total_optimizations": snapshot.total_optimizations,
        "total_cost_saved": snapshot.total_cost_saved
    }


@router.get("/snapshots/{year}/{month}")
def get_monthly_snapshot(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a monthly snapshot."""
    snapshot_service = SnapshotService(db)
    snapshot = snapshot_service.get_snapshot(current_user.company_id, year, month)
    
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snapshot not found"
        )
    
    return {
        "id": snapshot.id,
        "year": snapshot.year,
        "month": snapshot.month,
        "total_products": snapshot.total_products,
        "total_boxes": snapshot.total_boxes,
        "total_optimizations": snapshot.total_optimizations,
        "total_cost_saved": snapshot.total_cost_saved
    }
