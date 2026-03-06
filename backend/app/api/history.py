from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.optimization import OptimizationRunResponse, OptimizationSummary
from app.services.history_service import HistoryService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[OptimizationRunResponse])
def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get optimization run history for the authenticated user's company."""
    history_service = HistoryService(db)
    return history_service.get_optimization_history(current_user.company_id, skip, limit)


@router.get("/{run_id}", response_model=OptimizationSummary)
def get_run_details(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results for a specific optimization run."""
    history_service = HistoryService(db)
    return history_service.get_optimization_details(run_id, current_user.company_id)
