from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Order(Base):
    """
    Order model for multi-product order packing.
    Represents a customer order containing multiple products.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    order_number = Column(String(100), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    packing_results = relationship("OrderPackingResult", back_populates="order", cascade="all, delete-orphan")
    
    # Unique constraint on company_id + order_number
    __table_args__ = (
        {"schema": None},
    )


class OrderItem(Base):
    """
    OrderItem model linking orders to products with quantities.
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class OrderPackingResult(Base):
    """
    OrderPackingResult model storing packing results per box for an order.
    """
    __tablename__ = "order_packing_results"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    box_number = Column(Integer, nullable=False)  # Box 1, Box 2, etc.
    products_packed = Column(JSON, nullable=False)  # List of {product_id, quantity}
    total_weight = Column(Float, nullable=False)
    space_utilization = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    order = relationship("Order", back_populates="packing_results")
    box = relationship("Box")
