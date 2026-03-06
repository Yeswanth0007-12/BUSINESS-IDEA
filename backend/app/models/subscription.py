from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from app.core.enums import SubscriptionPlan, SubscriptionStatus


class SubscriptionPlanModel(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(SubscriptionPlan), unique=True, nullable=False)
    price_monthly = Column(Float, nullable=False)
    max_products = Column(Integer, nullable=False)
    max_boxes = Column(Integer, nullable=False)
    max_optimizations_per_month = Column(Integer, nullable=False)
    features = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    subscriptions = relationship("CompanySubscription", back_populates="plan")


class CompanySubscription(Base):
    __tablename__ = "company_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="subscription")
    plan = relationship("SubscriptionPlanModel", back_populates="subscriptions")
