"""
Analytics data models for tracking optimization metrics and trends.

This module contains models for:
- AnalyticsSnapshot: Daily snapshots of company analytics
- BoxUsageMetrics: Box usage tracking per period
- ShippingCostMetrics: Shipping cost analysis per period
"""

from datetime import date
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class AnalyticsSnapshot(Base):
    """Daily analytics snapshot for a company.
    
    Stores aggregated metrics for efficient historical trend analysis.
    One snapshot per company per day.
    """
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False, index=True)
    
    # Counts
    total_products = Column(Integer, nullable=False, default=0)
    total_boxes = Column(Integer, nullable=False, default=0)
    total_optimizations = Column(Integer, nullable=False, default=0)
    
    # Metrics
    avg_space_utilization = Column(Float, nullable=False, default=0.0)
    total_monthly_savings = Column(Float, nullable=False, default=0.0)
    total_annual_savings = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    company = relationship("Company", back_populates="analytics_snapshots")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'snapshot_date', name='uq_company_snapshot_date'),
        Index('idx_analytics_company_date', 'company_id', 'snapshot_date'),
    )
    
    def __repr__(self):
        return f"<AnalyticsSnapshot(company_id={self.company_id}, date={self.snapshot_date})>"


class BoxUsageMetrics(Base):
    """Box usage metrics for a specific period.
    
    Tracks how frequently each box is used and associated costs.
    """
    __tablename__ = "box_usage_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    
    # Period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Metrics
    usage_count = Column(Integer, nullable=False, default=0)
    total_cost = Column(Float, nullable=False, default=0.0)
    avg_utilization = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    company = relationship("Company", back_populates="box_usage_metrics")
    box = relationship("Box")
    
    # Indexes
    __table_args__ = (
        Index('idx_box_usage_company', 'company_id'),
        Index('idx_box_usage_period', 'period_start', 'period_end'),
    )
    
    def __repr__(self):
        return f"<BoxUsageMetrics(company_id={self.company_id}, box_id={self.box_id}, period={self.period_start} to {self.period_end})>"


class ShippingCostMetrics(Base):
    """Shipping cost metrics for a specific period.
    
    Tracks shipping costs, billable weights, and volumetric weight impact.
    """
    __tablename__ = "shipping_cost_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Metrics
    total_shipments = Column(Integer, nullable=False, default=0)
    total_shipping_cost = Column(Float, nullable=False, default=0.0)
    avg_billable_weight = Column(Float, nullable=False, default=0.0)
    volumetric_weight_percentage = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    company = relationship("Company", back_populates="shipping_cost_metrics")
    
    # Indexes
    __table_args__ = (
        Index('idx_shipping_cost_company', 'company_id'),
        Index('idx_shipping_cost_period', 'period_start', 'period_end'),
    )
    
    def __repr__(self):
        return f"<ShippingCostMetrics(company_id={self.company_id}, period={self.period_start} to {self.period_end})>"
