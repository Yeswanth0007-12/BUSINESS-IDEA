from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.models.product import Product
from app.models.box import Box
from app.models.optimization_run import OptimizationRun
from app.models.optimization_result import OptimizationResult as OptimizationResultModel
from app.schemas.analytics import (
    DashboardMetrics,
    LeakageInsight,
    InefficientProduct,
    SavingsTrend
)


class AnalyticsService:
    """Service for generating analytics and insights."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_metrics(self, company_id: int) -> DashboardMetrics:
        """
        Get dashboard metrics for a company.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            
        Returns:
            Dashboard metrics
        """
        # Count total products
        total_products = self.db.query(func.count(Product.id)).filter(
            Product.company_id == company_id
        ).scalar() or 0
        
        # Count total boxes
        total_boxes = self.db.query(func.count(Box.id)).filter(
            Box.company_id == company_id
        ).scalar() or 0
        
        # Get latest optimization run
        latest_run = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).order_by(desc(OptimizationRun.timestamp)).first()
        
        if latest_run:
            total_monthly_savings = latest_run.total_monthly_savings
            total_annual_savings = latest_run.total_annual_savings
            last_optimization_date = latest_run.timestamp
        else:
            total_monthly_savings = 0.0
            total_annual_savings = 0.0
            last_optimization_date = None
        
        # Count optimization runs
        optimization_runs_count = self.db.query(func.count(OptimizationRun.id)).filter(
            OptimizationRun.company_id == company_id
        ).scalar() or 0
        
        # Calculate average savings per product
        average_savings_per_product = (
            total_monthly_savings / total_products if total_products > 0 else 0.0
        )
        
        return DashboardMetrics(
            total_products=total_products,
            total_boxes=total_boxes,
            total_monthly_savings=total_monthly_savings,
            total_annual_savings=total_annual_savings,
            average_savings_per_product=average_savings_per_product,
            optimization_runs_count=optimization_runs_count,
            last_optimization_date=last_optimization_date
        )
    
    def get_leakage_insights(self, company_id: int) -> List[LeakageInsight]:
        """
        Get cost leakage insights by category (Pareto analysis).
        
        Args:
            company_id: Company ID for multi-tenant isolation
            
        Returns:
            List of leakage insights by category
        """
        # Get latest optimization run
        latest_run = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).order_by(desc(OptimizationRun.timestamp)).first()
        
        if not latest_run:
            return []
        
        # Query results grouped by product category
        results = self.db.query(
            Product.category,
            func.sum(OptimizationResultModel.savings).label('total_leakage'),
            func.count(OptimizationResultModel.id).label('product_count')
        ).join(
            OptimizationResultModel,
            Product.id == OptimizationResultModel.product_id
        ).filter(
            OptimizationResultModel.run_id == latest_run.id,
            Product.company_id == company_id
        ).group_by(
            Product.category
        ).order_by(
            desc('total_leakage')
        ).all()
        
        # Calculate total leakage for percentage
        total_leakage = sum(r.total_leakage for r in results)
        
        # Build insights
        insights = []
        for result in results:
            percentage = (result.total_leakage / total_leakage * 100) if total_leakage > 0 else 0
            insights.append(LeakageInsight(
                category=result.category,
                total_leakage=result.total_leakage,
                product_count=result.product_count,
                percentage_of_total=percentage
            ))
        
        return insights
    
    def get_top_inefficient_products(
        self,
        company_id: int,
        limit: int = 10
    ) -> List[InefficientProduct]:
        """
        Get top inefficient products with highest potential savings.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            limit: Maximum number of products to return
            
        Returns:
            List of inefficient products
        """
        # Get latest optimization run
        latest_run = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).order_by(desc(OptimizationRun.timestamp)).first()
        
        if not latest_run:
            return []
        
        # Query top products by savings
        results = self.db.query(
            Product.id,
            Product.name,
            Product.sku,
            OptimizationResultModel.current_cost,
            OptimizationResultModel.savings,
            OptimizationResultModel.savings_percentage
        ).join(
            OptimizationResultModel,
            Product.id == OptimizationResultModel.product_id
        ).filter(
            OptimizationResultModel.run_id == latest_run.id,
            Product.company_id == company_id
        ).order_by(
            desc(OptimizationResultModel.savings)
        ).limit(limit).all()
        
        # Build inefficient products list
        inefficient_products = []
        for result in results:
            inefficient_products.append(InefficientProduct(
                product_id=result.id,
                product_name=result.name,
                sku=result.sku,
                current_cost=result.current_cost,
                potential_savings=result.savings,
                savings_percentage=result.savings_percentage
            ))
        
        return inefficient_products
    
    def get_savings_trend(self, company_id: int, limit: int = 12) -> List[SavingsTrend]:
        """
        Get savings trend over time (last N optimization runs).
        
        Args:
            company_id: Company ID for multi-tenant isolation
            limit: Number of runs to include
            
        Returns:
            List of savings trends
        """
        # Query optimization runs ordered by date
        runs = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).order_by(
            desc(OptimizationRun.timestamp)
        ).limit(limit).all()
        
        # Build trend list (reverse to show oldest first)
        trends = []
        for run in reversed(runs):
            trends.append(SavingsTrend(
                date=run.timestamp,
                monthly_savings=run.total_monthly_savings,
                annual_savings=run.total_annual_savings
            ))
        
        return trends
