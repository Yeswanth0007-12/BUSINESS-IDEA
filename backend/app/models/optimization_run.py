from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    products_analyzed = Column(Integer, nullable=False)
    total_monthly_savings = Column(Float, nullable=False)
    total_annual_savings = Column(Float, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="optimization_runs")
    results = relationship("OptimizationResult", back_populates="run", cascade="all, delete-orphan")
