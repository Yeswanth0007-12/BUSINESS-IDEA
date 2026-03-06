from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from app.core.enums import UserRole


class UserRoleModel(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="role_assignment")
    assigner = relationship("User", foreign_keys=[granted_by])
