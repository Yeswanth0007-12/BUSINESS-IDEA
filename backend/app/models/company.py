from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    boxes = relationship("Box", back_populates="company", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="company", cascade="all, delete-orphan")
    optimization_tasks = relationship("OptimizationTask", back_populates="company", cascade="all, delete-orphan")
    subscription = relationship("CompanySubscription", back_populates="company", uselist=False)
    usage_records = relationship("UsageRecord", back_populates="company")
    audit_logs = relationship("AuditLog", back_populates="company")
    monthly_snapshots = relationship("MonthlySnapshot", back_populates="company")
    rate_limits = relationship("RateLimitRecord", back_populates="company")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="company", cascade="all, delete-orphan")
    box_usage_metrics = relationship("BoxUsageMetrics", back_populates="company", cascade="all, delete-orphan")
    shipping_cost_metrics = relationship("ShippingCostMetrics", back_populates="company", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="company", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="company", cascade="all, delete-orphan")


