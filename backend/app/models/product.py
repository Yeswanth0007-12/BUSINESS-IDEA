from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Product(Base):
    """
    Product model representing items to be packaged.
    
    Attributes:
        id: Unique product identifier
        company_id: Foreign key to company that owns this product
        name: Product name
        sku: Stock keeping unit (unique per company)
        category: Product category
        length_cm: Product length in centimeters
        width_cm: Product width in centimeters
        height_cm: Product height in centimeters
        weight_kg: Product weight in kilograms
        current_box_id: Currently assigned box (nullable)
        monthly_order_volume: Expected monthly order volume
        fragile: Whether product is fragile and requires special handling (default: False)
        stackable: Whether product can be stacked with other items (default: True)
        created_at: Timestamp when product was created
    """
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint('company_id', 'sku', name='uq_company_sku'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    length_cm = Column(Float, nullable=False)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    current_box_id = Column(Integer, ForeignKey("boxes.id"), nullable=True)
    monthly_order_volume = Column(Integer, nullable=False)
    fragile = Column(Boolean, default=False, nullable=False)
    stackable = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="products")
    current_box = relationship("Box", foreign_keys=[current_box_id])
