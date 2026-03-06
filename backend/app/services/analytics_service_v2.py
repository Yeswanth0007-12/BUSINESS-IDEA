"""
Advanced analytics service for optimization metrics and trends.

This service provides comprehensive analytics calculations including:
- Space utilization metrics
- Box usage frequency analysis
- Shipping cost analytics
- Time-series trend analysis
- Daily snapshot generation
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.optimization_run import OptimizationRun
from app.models.optimization_result import OptimizationResult
from app.models.product import Product
from app.models.box import Box
from app.models.analytics_snapshot import AnalyticsSnapshot


class AnalyticsServiceV2:
    """Advanced analytics service for optimization metrics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_space_utilization_metrics(
        self,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, float]:
        """Calculate space utilization metrics for a date range.
        
        Args:
            company_id: Company identifier
            start_date: Analysis period start
            end_date: Analysis period end
            
        Returns:
            Dictionary with avg_utilization, min_utilization, max_utilization, waste_percentage
        """
        # Query optimization results in date range
        results = self.db.query(OptimizationResult).join(
            OptimizationRun
        ).filter(
            and_(
                OptimizationRun.company_id == company_id,
                OptimizationRun.created_at >= datetime.combine(start_date, datetime.min.time()),
                OptimizationRun.created_at <= datetime.combine(end_date, datetime.max.time()),
                OptimizationResult.recommended_box_id.isnot(None)
            )
        ).all()
        
        if not results:
            return {
                "avg_utilization": 0.0,
                "min_utilization": 0.0,
                "max_utilization": 0.0,
                "waste_percentage": 100.0
            }
        
        # Calculate space utilization for each result
        utilizations = []
        for result in results:
            if result.product and result.recommended_box:
                # Calculate product volume
                product_volume = (
                    result.product.length_cm *
                    result.product.width_cm *
                    result.product.height_cm
                )
                
                # Calculate box volume
                box_volume = (
                    result.recommended_box.length_cm *
                    result.recommended_box.width_cm *
                    result.recommended_box.height_cm
                )
                
                if box_volume > 0:
                    utilization = (product_volume / box_volume) * 100
                    utilizations.append(utilization)
        
        if not utilizations:
            return {
                "avg_utilization": 0.0,
                "min_utilization": 0.0,
                "max_utilization": 0.0,
                "waste_percentage": 100.0
            }
        
        avg_utilization = sum(utilizations) / len(utilizations)
        min_utilization = min(utilizations)
        max_utilization = max(utilizations)
        waste_percentage = 100 - avg_utilization
        
        return {
            "avg_utilization": round(avg_utilization, 2),
            "min_utilization": round(min_utilization, 2),
            "max_utilization": round(max_utilization, 2),
            "waste_percentage": round(waste_percentage, 2)
        }
    
    def analyze_box_usage_frequency(
        self,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Analyze box usage frequency for a date range.
        
        Args:
            company_id: Company identifier
            start_date: Analysis period start
            end_date: Analysis period end
            
        Returns:
            List of box usage data sorted by usage_count descending
        """
        # Query optimization results
        results = self.db.query(OptimizationResult).join(
            OptimizationRun
        ).filter(
            and_(
                OptimizationRun.company_id == company_id,
                OptimizationRun.created_at >= datetime.combine(start_date, datetime.min.time()),
                OptimizationRun.created_at <= datetime.combine(end_date, datetime.max.time()),
                OptimizationResult.recommended_box_id.isnot(None)
            )
        ).all()
        
        # Count box usage
        box_usage = {}  # box_id -> count
        box_info = {}   # box_id -> box details
        box_utilizations = {}  # box_id -> list of utilizations
        
        for result in results:
            box_id = result.recommended_box_id
            
            if box_id not in box_usage:
                box_usage[box_id] = 0
                box_info[box_id] = result.recommended_box
                box_utilizations[box_id] = []
            
            box_usage[box_id] += 1
            
            # Calculate utilization for this result
            if result.product and result.recommended_box:
                product_volume = (
                    result.product.length_cm *
                    result.product.width_cm *
                    result.product.height_cm
                )
                box_volume = (
                    result.recommended_box.length_cm *
                    result.recommended_box.width_cm *
                    result.recommended_box.height_cm
                )
                if box_volume > 0:
                    utilization = (product_volume / box_volume) * 100
                    box_utilizations[box_id].append(utilization)
        
        # Calculate totals and percentages
        total_usage = sum(box_usage.values())
        usage_data = []
        
        for box_id, count in box_usage.items():
            box = box_info[box_id]
            percentage = (count / total_usage) * 100 if total_usage > 0 else 0
            total_cost = count * box.cost_per_unit
            
            # Calculate average utilization for this box
            utilizations = box_utilizations[box_id]
            avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0
            
            usage_data.append({
                "box_id": box_id,
                "box_name": box.name,
                "usage_count": count,
                "total_cost": round(total_cost, 2),
                "percentage": round(percentage, 2),
                "avg_utilization": round(avg_utilization, 2)
            })
        
        # Sort by usage count descending
        usage_data.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return usage_data
    
    def calculate_shipping_cost_metrics(
        self,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Calculate shipping cost metrics for a date range.
        
        Args:
            company_id: Company identifier
            start_date: Analysis period start
            end_date: Analysis period end
            
        Returns:
            Dictionary with shipping cost analytics
        """
        # Query optimization runs in date range
        runs = self.db.query(OptimizationRun).filter(
            and_(
                OptimizationRun.company_id == company_id,
                OptimizationRun.created_at >= datetime.combine(start_date, datetime.min.time()),
                OptimizationRun.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        ).all()
        
        if not runs:
            return {
                "total_shipments": 0,
                "total_shipping_cost": 0.0,
                "avg_shipping_cost_per_order": 0.0,
                "avg_billable_weight": 0.0,
                "volumetric_weight_percentage": 0.0,
                "actual_weight_percentage": 0.0
            }
        
        total_shipments = len(runs)
        total_shipping_cost = 0.0
        total_billable_weight = 0.0
        volumetric_exceeds_count = 0
        
        for run in runs:
            # Get the recommended result
            result = self.db.query(OptimizationResult).filter(
                and_(
                    OptimizationResult.optimization_run_id == run.id,
                    OptimizationResult.recommended_box_id.isnot(None)
                )
            ).first()
            
            if result and result.recommended_box and result.product:
                # Calculate volumetric weight
                box = result.recommended_box
                volumetric_weight = (
                    box.length_cm * box.width_cm * box.height_cm
                ) / 5000.0
                
                # Calculate billable weight
                actual_weight = result.product.weight_kg
                billable_weight = max(actual_weight, volumetric_weight)
                
                # Assume default courier rate of 2.5 per kg
                shipping_cost = billable_weight * 2.5
                
                total_shipping_cost += shipping_cost
                total_billable_weight += billable_weight
                
                if volumetric_weight > actual_weight:
                    volumetric_exceeds_count += 1
        
        avg_shipping_cost = total_shipping_cost / total_shipments if total_shipments > 0 else 0
        avg_billable_weight = total_billable_weight / total_shipments if total_shipments > 0 else 0
        volumetric_percentage = (volumetric_exceeds_count / total_shipments * 100) if total_shipments > 0 else 0
        actual_percentage = 100 - volumetric_percentage
        
        return {
            "total_shipments": total_shipments,
            "total_shipping_cost": round(total_shipping_cost, 2),
            "avg_shipping_cost_per_order": round(avg_shipping_cost, 2),
            "avg_billable_weight": round(avg_billable_weight, 2),
            "volumetric_weight_percentage": round(volumetric_percentage, 2),
            "actual_weight_percentage": round(actual_percentage, 2)
        }
    
    def calculate_savings_trend(
        self,
        company_id: int,
        months: int
    ) -> List[Dict[str, Any]]:
        """Calculate savings trend over specified number of months.
        
        Args:
            company_id: Company identifier
            months: Number of months to analyze (1-12)
            
        Returns:
            List of monthly trend data in chronological order
        """
        if months < 1 or months > 12:
            months = 6  # Default to 6 months
        
        trend_data = []
        current_date = date.today()
        
        for i in range(months):
            # Calculate month boundaries
            if i == 0:
                month_end = date(current_date.year, current_date.month, current_date.day)
                month_start = date(current_date.year, current_date.month, 1)
            else:
                # Go back i months
                month = current_date.month - i
                year = current_date.year
                while month <= 0:
                    month += 12
                    year -= 1
                
                month_start = date(year, month, 1)
                
                # Calculate last day of month
                if month == 12:
                    month_end = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            # Query optimizations for this month
            runs = self.db.query(OptimizationRun).filter(
                and_(
                    OptimizationRun.company_id == company_id,
                    OptimizationRun.created_at >= datetime.combine(month_start, datetime.min.time()),
                    OptimizationRun.created_at <= datetime.combine(month_end, datetime.max.time())
                )
            ).all()
            
            if runs:
                total_savings = sum(run.total_monthly_savings for run in runs if run.total_monthly_savings)
                count = len(runs)
                avg_savings = total_savings / count if count > 0 else 0
                
                trend_data.append({
                    "month": month_start.strftime("%Y-%m"),
                    "total_savings": round(total_savings, 2),
                    "optimization_count": count,
                    "avg_savings_per_optimization": round(avg_savings, 2)
                })
        
        # Reverse to chronological order (oldest first)
        trend_data.reverse()
        
        return trend_data
    
    def generate_daily_snapshot(
        self,
        company_id: int,
        snapshot_date: Optional[date] = None
    ) -> AnalyticsSnapshot:
        """Generate daily analytics snapshot for a company.
        
        Args:
            company_id: Company identifier
            snapshot_date: Date for snapshot (defaults to today)
            
        Returns:
            Created or updated AnalyticsSnapshot
        """
        if snapshot_date is None:
            snapshot_date = date.today()
        
        # Count total products
        total_products = self.db.query(Product).filter(
            Product.company_id == company_id
        ).count()
        
        # Count total boxes
        total_boxes = self.db.query(Box).filter(
            Box.company_id == company_id
        ).count()
        
        # Count total optimizations
        total_optimizations = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).count()
        
        # Calculate average space utilization from recent optimizations (last 30 days)
        thirty_days_ago = snapshot_date - timedelta(days=30)
        utilization_metrics = self.calculate_space_utilization_metrics(
            company_id,
            thirty_days_ago,
            snapshot_date
        )
        avg_space_utilization = utilization_metrics["avg_utilization"]
        
        # Calculate total savings from all optimizations
        runs = self.db.query(OptimizationRun).filter(
            OptimizationRun.company_id == company_id
        ).all()
        
        total_monthly_savings = sum(run.total_monthly_savings for run in runs if run.total_monthly_savings)
        total_annual_savings = total_monthly_savings * 12
        
        # Check if snapshot already exists for this date
        existing_snapshot = self.db.query(AnalyticsSnapshot).filter(
            and_(
                AnalyticsSnapshot.company_id == company_id,
                AnalyticsSnapshot.snapshot_date == snapshot_date
            )
        ).first()
        
        if existing_snapshot:
            # Update existing snapshot
            existing_snapshot.total_products = total_products
            existing_snapshot.total_boxes = total_boxes
            existing_snapshot.total_optimizations = total_optimizations
            existing_snapshot.avg_space_utilization = avg_space_utilization
            existing_snapshot.total_monthly_savings = total_monthly_savings
            existing_snapshot.total_annual_savings = total_annual_savings
            self.db.commit()
            self.db.refresh(existing_snapshot)
            return existing_snapshot
        else:
            # Create new snapshot
            snapshot = AnalyticsSnapshot(
                company_id=company_id,
                snapshot_date=snapshot_date,
                total_products=total_products,
                total_boxes=total_boxes,
                total_optimizations=total_optimizations,
                avg_space_utilization=avg_space_utilization,
                total_monthly_savings=total_monthly_savings,
                total_annual_savings=total_annual_savings
            )
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
            return snapshot
