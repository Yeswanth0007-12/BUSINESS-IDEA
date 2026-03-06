from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Box(Base):
    """
    Box model representing packaging containers.
    
    Attributes:
        id: Unique identifier
        company_id: Foreign key to company
        name: Box name/identifier
        length_cm: Box length in centimeters
        width_cm: Box width in centimeters
        height_cm: Box height in centimeters
        cost_per_unit: Cost per box unit
        usage_count: Number of times this box has been used
        max_weight_kg: Maximum weight capacity in kilograms (default: 30.0)
        material_type: Box material type - cardboard, plastic, or wood (default: "cardboard")
        created_at: Timestamp when box was created
    """
    __tablename__ = "boxes"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    length_cm = Column(Float, nullable=False)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    cost_per_unit = Column(Float, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    max_weight_kg = Column(Float, default=30.0, nullable=False)
    material_type = Column(String, default="cardboard", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="boxes")
