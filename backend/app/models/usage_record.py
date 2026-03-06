from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from app.core.enums import UsageAction


class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(SQLEnum(UsageAction), nullable=False, index=True)
    resource_type = Column(String, nullable=False)  # 'product', 'box', 'optimization'
    resource_id = Column(Integer, nullable=True)
    extra_data = Column(String, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="usage_records")
    user = relationship("User", back_populates="usage_records")
