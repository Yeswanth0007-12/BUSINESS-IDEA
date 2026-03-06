"""
Bulk Upload Models

Models for tracking bulk CSV uploads and individual order processing.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class BulkUpload(Base):
    """
    Tracks bulk CSV upload operations.
    
    Attributes:
        id: Primary key
        company_id: Foreign key to company
        filename: Original CSV filename
        total_orders: Total number of orders in the upload
        processed_orders: Number of successfully processed orders
        failed_orders: Number of failed orders
        status: Upload status (uploading, processing, completed, failed)
        created_at: Upload creation timestamp
        completed_at: Upload completion timestamp
    """
    __tablename__ = "bulk_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    total_orders = Column(Integer, default=0)
    processed_orders = Column(Integer, default=0)
    failed_orders = Column(Integer, default=0)
    status = Column(String(50), default="uploading", index=True)  # uploading, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("BulkUploadOrder", back_populates="upload", cascade="all, delete-orphan")


class BulkUploadOrder(Base):
    """
    Tracks individual orders within a bulk upload.
    
    Attributes:
        id: Primary key
        upload_id: Foreign key to bulk_upload
        row_number: Row number in the CSV file
        order_data: JSON containing order details
        status: Order processing status (pending, processing, completed, failed)
        task_id: Celery task ID for async processing
        error_message: Error message if processing failed
    """
    __tablename__ = "bulk_upload_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("bulk_uploads.id"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    order_data = Column(JSON, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    task_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    upload = relationship("BulkUpload", back_populates="orders")
