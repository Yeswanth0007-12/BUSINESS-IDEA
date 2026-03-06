"""
API Key model for warehouse integration authentication.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiKey(Base):
    """
    API Key model for warehouse system authentication.
    
    Stores SHA-256 hashed API keys for secure authentication.
    Keys are scoped to a single company for multi-tenant isolation.
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    key_hash = Column(String(255), nullable=False, unique=True)  # SHA-256 hash
    name = Column(String(100), nullable=False)  # Descriptive name for the key
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationship
    company = relationship("Company", back_populates="api_keys")
