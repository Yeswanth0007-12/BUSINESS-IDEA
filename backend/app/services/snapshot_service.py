from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from typing import Optional
import json

from app.models.monthly_snapshot import MonthlySnapshot
from app.models.product import Product
from app.models.box import Box
from app.models.optimization_run import OptimizationRun


class SnapshotService:
    """Monthly snapshot generation service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_monthly_snapshot(self, company_id: int, year: int, month: int) -> MonthlySnapshot:
        """Generate a monthly snapshot for a company."""
        # Check if snapshot already exists
        existing = self.db.query(MonthlySnapshot).filter(
            MonthlySnapshot.company_id == company_id,
            MonthlySnapshot.year == year,
            MonthlySnapshot.month == month
        ).first()
        
        if existing:
            return existing
        
        # Count resources
        total_products = self.db.query(func.count(Product.id)).filter(
            Product.company_id == company_id,
            extract('year', Product.created_at) <= year,
            extract('month', Product.created_at) <= month
        ).scalar() or 0
        
        total_boxes = self.db.query(func.count(Box.id)).filter(
            Box.company_id == company_id,
            extract('year', Box.created_at) <= year,
            extract('month', Box.created_at) <= month
        ).scalar() or 0
        
        # Count optimizations for the month
        total_optimizations = self.db.query(func.count(OptimizationRun.id)).filter(
            OptimizationRun.company_id == company_id,
            extract('year', OptimizationRun.timestamp) == year,
            extract('month', OptimizationRun.timestamp) == month
        ).scalar() or 0
        
        # Calculate total cost saved
        cost_saved_result = self.db.query(func.sum(OptimizationRun.total_monthly_savings)).filter(
            OptimizationRun.company_id == company_id,
            extract('year', OptimizationRun.timestamp) == year,
            extract('month', OptimizationRun.timestamp) == month
        ).scalar()
        
        total_cost_saved = int(cost_saved_result) if cost_saved_result else 0
        
        # Create snapshot
        snapshot = MonthlySnapshot(
            company_id=company_id,
            year=year,
            month=month,
            total_products=total_products,
            total_boxes=total_boxes,
            total_optimizations=total_optimizations,
            total_cost_saved=total_cost_saved,
            extra_metrics=json.dumps({
                'generated_at': datetime.utcnow().isoformat()
            })
        )
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot
    
    def get_snapshot(self, company_id: int, year: int, month: int) -> Optional[MonthlySnapshot]:
        """Get a monthly snapshot."""
        return self.db.query(MonthlySnapshot).filter(
            MonthlySnapshot.company_id == company_id,
            MonthlySnapshot.year == year,
            MonthlySnapshot.month == month
        ).first()
