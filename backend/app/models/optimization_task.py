"""
OptimizationTask model for tracking asynchronous optimization tasks.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.base import Base


class OptimizationTask(Base):
    """
    Model for tracking asynchronous optimization task status and progress.
    
    Attributes:
        id: Unique UUID identifier for the task
        company_id: Company that owns this task
        task_type: Type of optimization (single, bulk, order)
        status: Current task status (pending, processing, completed, failed)
        progress: Task progress percentage (0-100)
        created_at: When the task was created
        started_at: When the task started processing
        completed_at: When the task completed or failed
        result_id: Foreign key to OptimizationRun if completed successfully
        error_message: Error details if task failed
        metadata: Additional task information as JSON
    """
    __tablename__ = "optimization_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    task_type = Column(String(50), nullable=False)  # single, bulk, order
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    task_metadata = Column(JSON, nullable=True)  # Renamed from metadata (reserved by SQLAlchemy)
    
    # Relationships
    company = relationship("Company", back_populates="optimization_tasks")
    result = relationship("OptimizationRun", foreign_keys=[result_id])
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_optimization_tasks_company_status", "company_id", "status"),
        Index("idx_optimization_tasks_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<OptimizationTask(id={self.id}, status={self.status}, progress={self.progress})>"
