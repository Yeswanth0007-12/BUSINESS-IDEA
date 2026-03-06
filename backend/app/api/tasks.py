"""
API endpoints for task status tracking and result retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.optimization_task import OptimizationTask
from app.models.optimization_run import OptimizationRun
from app.models.optimization_result import OptimizationResult as OptimizationResultModel
from app.schemas.task import TaskStatusResponse, TaskResultResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of an asynchronous optimization task.
    
    Returns task status, progress, and result_id when completed.
    
    Args:
        task_id: UUID of the task to check
        
    Returns:
        TaskStatusResponse with current status and progress
        
    Raises:
        404: Task not found or doesn't belong to user's company
    """
    # Query task with company filtering for multi-tenant isolation
    task = db.query(OptimizationTask).filter(
        OptimizationTask.id == task_id,
        OptimizationTask.company_id == current_user.company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return TaskStatusResponse(
        task_id=task.id,
        task_type=task.task_type,
        status=task.status,
        progress=task.progress,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        result_id=task.result_id,
        error_message=task.error_message,
        metadata=task.metadata
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
def get_task_result(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the results of a completed optimization task.
    
    Args:
        task_id: UUID of the task
        
    Returns:
        TaskResultResponse with optimization results
        
    Raises:
        404: Task not found, not completed, or doesn't belong to user's company
    """
    # Query task with company filtering
    task = db.query(OptimizationTask).filter(
        OptimizationTask.id == task_id,
        OptimizationTask.company_id == current_user.company_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Check if task is completed
    if task.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is not completed yet. Current status: {task.status}"
        )
    
    # Check if result exists
    if not task.result_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task completed but no result found"
        )
    
    # Fetch optimization run and results
    optimization_run = db.query(OptimizationRun).filter(
        OptimizationRun.id == task.result_id
    ).first()
    
    if not optimization_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization result not found"
        )
    
    # Fetch detailed results
    results = db.query(OptimizationResultModel).filter(
        OptimizationResultModel.run_id == optimization_run.id
    ).all()
    
    # Build result dictionary
    result_data = {
        "run_id": optimization_run.id,
        "total_products_analyzed": optimization_run.products_analyzed,
        "total_monthly_savings": optimization_run.total_monthly_savings,
        "total_annual_savings": optimization_run.total_annual_savings,
        "timestamp": optimization_run.timestamp.isoformat() if optimization_run.timestamp else None,
        "results_count": len(results),
        "results": [
            {
                "product_id": r.product_id,
                "current_box_id": r.current_box_id,
                "recommended_box_id": r.recommended_box_id,
                "savings": r.savings,
                "savings_percentage": r.savings_percentage,
                "space_utilization": r.space_utilization,
                "total_cost_current": r.total_cost_current,
                "total_cost_recommended": r.total_cost_recommended
            }
            for r in results
        ]
    }
    
    return TaskResultResponse(
        task_id=task.id,
        status=task.status,
        result=result_data
    )
