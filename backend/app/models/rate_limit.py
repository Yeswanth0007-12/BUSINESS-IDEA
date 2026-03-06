from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class RateLimitRecord(Base):
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    endpoint = Column(String, nullable=False, index=True)
    request_count = Column(Integer, nullable=False, default=1)
    window_start = Column(DateTime, nullable=False, index=True)
    window_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="rate_limits")
