from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class OptimizationResult(Base):
    __tablename__ = "optimization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_box_id = Column(Integer, ForeignKey("boxes.id"), nullable=True)
    recommended_box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    current_cost = Column(Float, nullable=False)
    recommended_cost = Column(Float, nullable=False)
    savings = Column(Float, nullable=False)
    savings_percentage = Column(Float, nullable=False)
    volumetric_weight_current = Column(Float, nullable=False)
    volumetric_weight_recommended = Column(Float, nullable=False)
    # Phase 2: Advanced Packing Engine fields
    orientation_length = Column(Float, nullable=True)
    orientation_width = Column(Float, nullable=True)
    orientation_height = Column(Float, nullable=True)
    space_utilization = Column(Float, nullable=False, default=0.0)
    unused_volume = Column(Float, nullable=False, default=0.0)
    # Phase 3: Shipping Cost fields
    shipping_cost_current = Column(Float, nullable=False, default=0.0)
    shipping_cost_recommended = Column(Float, nullable=False, default=0.0)
    total_cost_current = Column(Float, nullable=False, default=0.0)
    total_cost_recommended = Column(Float, nullable=False, default=0.0)
    billable_weight_current = Column(Float, nullable=False, default=0.0)
    billable_weight_recommended = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    run = relationship("OptimizationRun", back_populates="results")
    product = relationship("Product")
    current_box = relationship("Box", foreign_keys=[current_box_id])
    recommended_box = relationship("Box", foreign_keys=[recommended_box_id])
