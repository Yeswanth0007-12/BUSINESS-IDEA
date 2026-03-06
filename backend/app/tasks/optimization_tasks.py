"""
Celery tasks for asynchronous optimization processing.
"""
from celery import Task
from datetime import datetime
from typing import Dict, Any
import logging
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.optimization_task import OptimizationTask
from app.services.optimization_engine import OptimizationEngine
from app.schemas.optimization import OptimizationRequest

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


def update_task_status(
    db,
    task_id: str,
    status: str,
    progress: int = None,
    error_message: str = None,
    result_id: int = None
):
    """
    Update optimization task status in database.
    
    Args:
        db: Database session
        task_id: UUID of the task
        status: New status (pending, processing, completed, failed)
        progress: Progress percentage (0-100)
        error_message: Error details if failed
        result_id: ID of optimization result if completed
    """
    try:
        task = db.query(OptimizationTask).filter(
            OptimizationTask.id == UUID(task_id)
        ).first()
        
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return
        
        task.status = status
        
        if progress is not None:
            task.progress = progress
        
        if status == "processing" and not task.started_at:
            task.started_at = datetime.utcnow()
        
        if status in ["completed", "failed"]:
            task.completed_at = datetime.utcnow()
            task.progress = 100 if status == "completed" else task.progress
        
        if error_message:
            task.error_message = error_message
        
        if result_id:
            task.result_id = result_id
        
        db.commit()
        logger.info(f"Task {task_id} updated: status={status}, progress={progress}")
        
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}")
        db.rollback()


@celery_app.task(bind=True, base=DatabaseTask, name="app.tasks.optimization_tasks.optimize_packaging_task")
def optimize_packaging_task(
    self,
    task_id: str,
    company_id: int,
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Asynchronous Celery task for packaging optimization.
    
    Args:
        task_id: Unique task identifier (UUID string)
        company_id: Company ID for multi-tenant isolation
        request_data: Optimization request parameters as dict
        
    Returns:
        Dictionary with optimization results
        
    Raises:
        Exception: If optimization fails
    """
    db = None
    
    try:
        logger.info(f"Starting optimization task {task_id} for company {company_id}")
        
        # Get database session
        db = SessionLocal()
        
        # Update status to processing
        update_task_status(db, task_id, "processing", progress=0)
        
        # Parse request data
        request = OptimizationRequest(**request_data)
        
        # Update progress
        update_task_status(db, task_id, "processing", progress=25)
        
        # Initialize optimization engine
        engine = OptimizationEngine(db)
        
        # Extract courier_rate from request_data if present
        courier_rate = request_data.get("courier_rate", 2.5)
        
        # Run optimization
        logger.info(f"Running optimization for company {company_id}")
        result = engine.optimize_packaging(company_id, request, courier_rate=courier_rate)
        
        # Update progress
        update_task_status(db, task_id, "processing", progress=75)
        
        # Convert result to dict for storage
        result_dict = {
            "total_products_analyzed": result.total_products_analyzed,
            "products_with_savings": result.products_with_savings,
            "total_monthly_savings": result.total_monthly_savings,
            "total_annual_savings": result.total_annual_savings,
            "run_id": result.run_id,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None,
            "results_count": len(result.results)
        }
        
        # Update status to completed with result_id
        update_task_status(
            db,
            task_id,
            "completed",
            progress=100,
            result_id=result.run_id
        )
        
        logger.info(f"Task {task_id} completed successfully. Run ID: {result.run_id}")
        
        return result_dict
        
    except Exception as e:
        error_msg = f"Optimization failed: {str(e)}"
        logger.error(f"Task {task_id} failed: {error_msg}", exc_info=True)
        
        # Update status to failed
        if db:
            update_task_status(db, task_id, "failed", error_message=error_msg)
        
        # Re-raise exception for Celery to handle
        raise
        
    finally:
        # Close database session
        if db:
            db.close()


@celery_app.task(bind=True, base=DatabaseTask, name="app.tasks.optimization_tasks.optimize_order_packing_task")
def optimize_order_packing_task(
    self,
    order_id: int,
    company_id: int
) -> Dict[str, Any]:
    """
    Simplified Celery task for order packing (used by bulk upload).
    
    Args:
        order_id: Order ID to optimize
        company_id: Company ID for multi-tenant isolation
        
    Returns:
        Dictionary with packing results
        
    Raises:
        Exception: If optimization fails
    """
    db = None
    
    try:
        logger.info(f"Starting order packing for order {order_id}")
        
        # Get database session
        db = SessionLocal()
        
        # Import here to avoid circular imports
        from app.services.order_service import OrderService
        
        # Initialize order service
        order_service = OrderService(db)
        
        # Run order optimization
        logger.info(f"Running order optimization for order {order_id}")
        result = order_service.optimize_order_packing(order_id, company_id)
        
        # Convert result to dict
        result_dict = {
            "order_id": order_id,
            "total_boxes": result.get("total_boxes", 0),
            "total_cost": result.get("total_cost", 0.0),
            "success": result.get("success", False),
            "boxes_used": len(result.get("boxes_used", []))
        }
        
        logger.info(f"Order packing for order {order_id} completed successfully")
        
        return result_dict
        
    except Exception as e:
        error_msg = f"Order packing failed: {str(e)}"
        logger.error(f"Order {order_id} failed: {error_msg}", exc_info=True)
        
        # Re-raise exception
        raise
        
    finally:
        # Close database session
        if db:
            db.close()

def optimize_order_task(
    self,
    task_id: str,
    company_id: int,
    order_id: int
) -> Dict[str, Any]:
    """
    Asynchronous Celery task for multi-product order optimization.
    
    Args:
        task_id: Unique task identifier (UUID string)
        company_id: Company ID for multi-tenant isolation
        order_id: Order ID to optimize
        
    Returns:
        Dictionary with packing results
        
    Raises:
        Exception: If optimization fails
    """
    db = None
    
    try:
        logger.info(f"Starting order optimization task {task_id} for order {order_id}")
        
        # Get database session
        db = SessionLocal()
        
        # Update status to processing
        update_task_status(db, task_id, "processing", progress=0)
        
        # Import here to avoid circular imports
        from app.services.order_service import OrderService
        
        # Initialize order service
        order_service = OrderService(db)
        
        # Update progress
        update_task_status(db, task_id, "processing", progress=25)
        
        # Run order optimization
        logger.info(f"Running order optimization for order {order_id}")
        result = order_service.optimize_order_packing(order_id, company_id)
        
        # Update progress
        update_task_status(db, task_id, "processing", progress=75)
        
        # Convert result to dict
        result_dict = {
            "order_id": order_id,
            "total_boxes": result.get("total_boxes", 0),
            "total_cost": result.get("total_cost", 0.0),
            "success": result.get("success", False),
            "boxes_used": len(result.get("boxes_used", []))
        }
        
        # Update status to completed
        update_task_status(
            db,
            task_id,
            "completed",
            progress=100
        )
        
        logger.info(f"Order task {task_id} completed successfully")
        
        return result_dict
        
    except Exception as e:
        error_msg = f"Order optimization failed: {str(e)}"
        logger.error(f"Task {task_id} failed: {error_msg}", exc_info=True)
        
        # Update status to failed
        if db:
            update_task_status(db, task_id, "failed", error_message=error_msg)
        
        # Re-raise exception
        raise
        
    finally:
        # Close database session
        if db:
            db.close()
