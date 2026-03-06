"""
Webhook models for warehouse integration event notifications.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Webhook(Base):
    """
    Webhook model for event notification configuration.
    
    Stores webhook URLs and event subscriptions for warehouse systems.
    Webhooks are scoped to a single company for multi-tenant isolation.
    """
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    url = Column(String(500), nullable=False)  # HTTPS endpoint URL
    events = Column(JSON, nullable=False)  # List of subscribed event types
    secret = Column(String(255), nullable=False)  # Secret for HMAC signature
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")


class WebhookDelivery(Base):
    """
    Webhook delivery tracking model.
    
    Records each webhook delivery attempt including status and response.
    Used for retry logic and debugging webhook issues.
    """
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False, index=True)
    event = Column(String(100), nullable=False)  # Event type (e.g., "optimization.completed")
    payload = Column(JSON, nullable=False)  # Event payload
    status = Column(String(50), nullable=False)  # pending, success, failed
    response_code = Column(Integer, nullable=True)  # HTTP response code
    response_body = Column(Text, nullable=True)  # HTTP response body
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    delivered_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Relationship
    webhook = relationship("Webhook", back_populates="deliveries")
