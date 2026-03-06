from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.export_service import ExportService
from app.models.user import User


router = APIRouter(prefix="/export", tags=["export"])


@router.get("/products")
def export_products(
    format: str = 'csv',
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export products to CSV."""
    export_service = ExportService(db)
    csv_data = export_service.export_products(current_user.company_id, format)
    
    return Response(
        content=csv_data,
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=products_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        }
    )


@router.get("/boxes")
def export_boxes(
    format: str = 'csv',
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export boxes to CSV."""
    export_service = ExportService(db)
    csv_data = export_service.export_boxes(current_user.company_id, format)
    
    return Response(
        content=csv_data,
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=boxes_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        }
    )


@router.get("/optimizations")
def export_optimizations(
    format: str = 'csv',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export optimization runs to CSV."""
    export_service = ExportService(db)
    csv_data = export_service.export_optimizations(
        current_user.company_id,
        format,
        start_date,
        end_date
    )
    
    return Response(
        content=csv_data,
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=optimizations_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        }
    )


@router.get("/audit-logs")
def export_audit_logs(
    format: str = 'csv',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export audit logs to CSV."""
    export_service = ExportService(db)
    csv_data = export_service.export_audit_logs(
        current_user.company_id,
        format,
        start_date,
        end_date
    )
    
    return Response(
        content=csv_data,
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=audit_logs_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        }
    )
