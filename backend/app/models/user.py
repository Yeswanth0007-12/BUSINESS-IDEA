from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="users")
    role_assignment = relationship("UserRoleModel", foreign_keys="UserRoleModel.user_id", back_populates="user", uselist=False)
    usage_records = relationship("UsageRecord", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


