from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from app.core.enums import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=True)
    changes = Column(String, nullable=True)  # JSON string of before/after
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
