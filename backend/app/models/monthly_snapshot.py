from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class MonthlySnapshot(Base):
    __tablename__ = "monthly_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    total_products = Column(Integer, nullable=False, default=0)
    total_boxes = Column(Integer, nullable=False, default=0)
    total_optimizations = Column(Integer, nullable=False, default=0)
    total_cost_saved = Column(Integer, nullable=False, default=0)
    extra_metrics = Column(String, nullable=True)  # JSON string for detailed metrics
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="monthly_snapshots")
