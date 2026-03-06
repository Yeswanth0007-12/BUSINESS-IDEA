from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.optimization_task import OptimizationTask
from app.schemas.optimization import OptimizationRequest, OptimizationSummary
from app.schemas.task import TaskSubmitResponse
from app.services.optimization_engine import OptimizationEngine
from app.services.auth_service import get_current_user
from app.tasks.optimization_tasks import optimize_packaging_task

router = APIRouter(prefix="/optimize", tags=["Optimization"])


@router.post("", response_model=OptimizationSummary)
def run_optimization(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run packaging optimization for products synchronously.
    
    Accepts optional courier_rate parameter (default: 2.5 per kg).
    Rate limiting should be applied to this endpoint in production.
    """
    optimization_engine = OptimizationEngine(db)
    return optimization_engine.optimize_packaging(
        current_user.company_id, 
        request, 
        courier_rate=request.courier_rate
    )


@router.post("/async", response_model=TaskSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
def run_optimization_async(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Queue packaging optimization for asynchronous processing.
    
    Returns immediately with a task_id that can be used to check status
    and retrieve results when complete.
    
    Use GET /tasks/{task_id} to check status.
    Use GET /tasks/{task_id}/result to retrieve results when completed.
    """
    # Generate unique task ID
    task_id = uuid.uuid4()
    
    # Create task record in database
    task = OptimizationTask(
        id=task_id,
        company_id=current_user.company_id,
        task_type="single",
        status="pending",
        progress=0,
        created_at=datetime.utcnow(),
        metadata={
            "product_ids": request.product_ids,
            "courier_rate": request.courier_rate
        }
    )
    db.add(task)
    db.commit()
    
    # Queue Celery task
    request_data = {
        "product_ids": request.product_ids,
        "courier_rate": request.courier_rate
    }
    
    optimize_packaging_task.apply_async(
        args=[str(task_id), current_user.company_id, request_data],
        task_id=str(task_id)
    )
    
    return TaskSubmitResponse(
        task_id=task_id,
        status="pending",
        message="Optimization task queued successfully"
    )
