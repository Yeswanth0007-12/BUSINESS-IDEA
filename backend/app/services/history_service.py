from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.models.optimization_run import OptimizationRun
from app.models.optimization_result import OptimizationResult as OptimizationResultModel
from app.models.product import Product
from app.models.box import Box
from app.schemas.optimization import OptimizationRunResponse, OptimizationResult, OptimizationSummary


class HistoryService:
    """Service for managing optimization history."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_optimization_history(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[OptimizationRunResponse]:
        """
        Get optimization run history for a company.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of optimization runs
        """
        runs = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).order_by(
            desc(OptimizationRun.timestamp)
        ).offset(skip).limit(limit).all()
        
        return [OptimizationRunResponse.model_validate(run) for run in runs]
    
    def get_optimization_details(
        self,
        run_id: int,
        company_id: int
    ) -> OptimizationSummary:
        """
        Get detailed results for a specific optimization run.
        
        Args:
            run_id: Optimization run ID
            company_id: Company ID for ownership verification
            
        Returns:
            Optimization summary with detailed results
            
        Raises:
            HTTPException: If run not found or doesn't belong to company
        """
        # Get optimization run with ownership verification
        run = self.db.query(OptimizationRun).filter(
            OptimizationRun.id == run_id,
            OptimizationRun.company_id == company_id
        ).first()
        
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Optimization run not found"
            )
        
        # Get all results for this run
        result_records = self.db.query(OptimizationResultModel).filter(
            OptimizationResultModel.run_id == run_id
        ).all()
        
        # Build detailed results list
        results = []
        products_with_savings = 0
        
        for record in result_records:
            # Get product and box details
            product = self.db.query(Product).filter(Product.id == record.product_id).first()
            current_box = self.db.query(Box).filter(Box.id == record.current_box_id).first()
            recommended_box = self.db.query(Box).filter(Box.id == record.recommended_box_id).first()
            
            if product and current_box and recommended_box:
                results.append(OptimizationResult(
                    product_id=product.id,
                    product_name=product.name,
                    current_box_id=current_box.id,
                    current_box_name=current_box.name,
                    current_cost=record.current_cost,
                    recommended_box_id=recommended_box.id,
                    recommended_box_name=recommended_box.name,
                    recommended_cost=record.recommended_cost,
                    savings=record.savings,
                    savings_percentage=record.savings_percentage,
                    volumetric_weight_current=record.volumetric_weight_current,
                    volumetric_weight_recommended=record.volumetric_weight_recommended
                ))
                
                if record.savings > 0:
                    products_with_savings += 1
        
        return OptimizationSummary(
            total_products_analyzed=run.products_analyzed,
            products_with_savings=products_with_savings,
            total_monthly_savings=run.total_monthly_savings,
            total_annual_savings=run.total_annual_savings,
            results=results,
            run_id=run.id,
            timestamp=run.timestamp
        )
