"""
Bulk Upload API Endpoints

API endpoints for bulk CSV upload of orders.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..services.auth_service import get_current_user
from ..models.user import User
from ..models.bulk_upload import BulkUpload
from ..schemas.bulk_upload import (
    BulkUploadResponse,
    BulkUploadSummary,
    BulkUploadFailedOrdersResponse,
    BulkUploadOrderResponse
)
from ..services.bulk_upload_service import BulkUploadService


router = APIRouter(prefix="/api/v1/bulk-upload", tags=["bulk-upload"])


@router.post("", response_model=BulkUploadSummary, status_code=status.HTTP_202_ACCEPTED)
async def upload_bulk_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a CSV file containing multiple orders for bulk processing.
    
    CSV Format:
    - Required columns: order_number, customer_name, product_sku, quantity
    - Maximum file size: 10 MB
    - Maximum rows: 10,000
    
    The endpoint will:
    1. Validate the CSV format and data
    2. Create order records for valid orders
    3. Queue optimization tasks for each order
    4. Return a summary with task IDs for tracking
    
    Args:
        file: CSV file upload
        db: Database session
        current_user: Authenticated user
        
    Returns:
        BulkUploadSummary with processing results
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file"
        )
    
    # Create bulk upload record
    bulk_upload = BulkUpload(
        company_id=current_user.company_id,
        filename=file.filename,
        status="uploading"
    )
    db.add(bulk_upload)
    db.commit()
    db.refresh(bulk_upload)
    
    # Process upload
    service = BulkUploadService(db)
    
    try:
        result = await service.process_bulk_upload(
            upload_id=bulk_upload.id,
            csv_file=file,
            company_id=current_user.company_id
        )
        
        return BulkUploadSummary(
            upload_id=result["upload_id"],
            total_orders=result["total_orders"],
            successful=result["successful"],
            failed=result["failed"],
            task_ids=result["task_ids"],
            status=result["status"],
            message=f"Bulk upload processed: {result['successful']} orders queued, {result['failed']} failed",
            failed_details=result.get("failed_details", [])  # Include detailed failure info
        )
        
    except HTTPException:
        # Update upload status to failed
        bulk_upload.status = "failed"
        db.commit()
        raise
    except Exception as e:
        # Update upload status to failed
        bulk_upload.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing bulk upload: {str(e)}")


@router.get("/{upload_id}", response_model=BulkUploadResponse)
def get_bulk_upload_status(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a bulk upload.
    
    Args:
        upload_id: Bulk upload ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        BulkUploadResponse with upload status
    """
    service = BulkUploadService(db)
    upload = service.get_bulk_upload_status(upload_id, current_user.company_id)
    
    return upload


@router.get("/{upload_id}/failed", response_model=BulkUploadFailedOrdersResponse)
def get_failed_orders(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get failed orders for a bulk upload.
    
    Args:
        upload_id: Bulk upload ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        BulkUploadFailedOrdersResponse with failed order details
    """
    service = BulkUploadService(db)
    failed_orders = service.get_failed_orders(upload_id, current_user.company_id)
    
    return BulkUploadFailedOrdersResponse(
        upload_id=upload_id,
        failed_count=len(failed_orders),
        failed_orders=[BulkUploadOrderResponse.from_orm(order) for order in failed_orders]
    )
