from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    DashboardMetrics,
    LeakageInsight,
    InefficientProduct,
    SavingsTrend
)
from app.services.analytics_service import AnalyticsService
from app.services.analytics_service_v2 import AnalyticsServiceV2
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for the authenticated user's company."""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_metrics(current_user.company_id)


@router.get("/leakage", response_model=List[LeakageInsight])
def get_leakage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cost leakage insights by category (Pareto analysis)."""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_leakage_insights(current_user.company_id)


@router.get("/inefficient", response_model=List[InefficientProduct])
def get_inefficient(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top inefficient products with highest potential savings."""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_top_inefficient_products(current_user.company_id, limit)


@router.get("/trends", response_model=List[SavingsTrend])
def get_trends(
    limit: int = Query(12, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get savings trend over time."""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_savings_trend(current_user.company_id, limit)


# Phase 8: Enhanced Dashboard APIs

@router.get("/summary")
def get_analytics_summary(
    period: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics summary for the company.
    
    Returns total products, boxes, optimizations, savings, and space utilization metrics.
    Target response time: < 200ms at p95.
    """
    analytics_service_v2 = AnalyticsServiceV2(db)
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    
    # Get space utilization metrics
    utilization_metrics = analytics_service_v2.calculate_space_utilization_metrics(
        current_user.company_id,
        start_date,
        end_date
    )
    
    # Get counts from database
    from app.models.product import Product
    from app.models.box import Box
    from app.models.optimization_run import OptimizationRun
    
    total_products = db.query(Product).filter(
        Product.company_id == current_user.company_id
    ).count()
    
    total_boxes = db.query(Box).filter(
        Box.company_id == current_user.company_id
    ).count()
    
    total_optimizations = db.query(OptimizationRun).filter(
        OptimizationRun.company_id == current_user.company_id
    ).count()
    
    # Calculate total savings
    runs = db.query(OptimizationRun).filter(
        OptimizationRun.company_id == current_user.company_id
    ).all()
    
    total_monthly_savings = sum(run.total_monthly_savings for run in runs if run.total_monthly_savings)
    total_annual_savings = total_monthly_savings * 12
    
    return {
        "total_products": total_products,
        "total_boxes": total_boxes,
        "total_optimizations": total_optimizations,
        "total_monthly_savings": round(total_monthly_savings, 2),
        "total_annual_savings": round(total_annual_savings, 2),
        "avg_space_utilization": utilization_metrics["avg_utilization"],
        "waste_percentage": utilization_metrics["waste_percentage"],
        "period_days": period
    }


@router.get("/box-usage")
def get_box_usage(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get box usage frequency and cost analysis.
    
    Returns box usage data sorted by usage_count descending.
    Target response time: < 200ms at p95.
    """
    analytics_service_v2 = AnalyticsServiceV2(db)
    
    # Default to last 30 days if not specified
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    usage_data = analytics_service_v2.analyze_box_usage_frequency(
        current_user.company_id,
        start_date,
        end_date
    )
    
    total_usage = sum(item["usage_count"] for item in usage_data)
    total_cost = sum(item["total_cost"] for item in usage_data)
    
    return {
        "boxes": usage_data,
        "total_usage": total_usage,
        "total_cost": round(total_cost, 2)
    }


@router.get("/shipping-cost")
def get_shipping_cost(
    period: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shipping cost analytics with volumetric weight breakdown.
    
    Returns shipping cost metrics including billable weight and volumetric weight impact.
    Target response time: < 200ms at p95.
    """
    analytics_service_v2 = AnalyticsServiceV2(db)
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    
    metrics = analytics_service_v2.calculate_shipping_cost_metrics(
        current_user.company_id,
        start_date,
        end_date
    )
    
    return metrics


@router.get("/trends-v2")
def get_trends_v2(
    months: int = Query(6, ge=1, le=12, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time-series trend data for savings and optimizations.
    
    Returns monthly trend data in chronological order.
    Target response time: < 200ms at p95.
    """
    analytics_service_v2 = AnalyticsServiceV2(db)
    
    trend_data = analytics_service_v2.calculate_savings_trend(
        current_user.company_id,
        months
    )
    
    return {
        "trends": trend_data
    }
