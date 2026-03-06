from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.box import Box
from app.schemas.box import BoxCreate, BoxUpdate, BoxResponse


class BoxService:
    """Service for managing boxes with multi-tenant isolation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_box(self, box_data: BoxCreate, company_id: int) -> Box:
        """
        Create a new box.
        
        Args:
            box_data: Box creation data
            company_id: Company ID for multi-tenant isolation
            
        Returns:
            Created box
        """
        new_box = Box(
            company_id=company_id,
            name=box_data.name,
            length_cm=box_data.length_cm,
            width_cm=box_data.width_cm,
            height_cm=box_data.height_cm,
            cost_per_unit=box_data.cost_per_unit,
            usage_count=0
        )
        
        self.db.add(new_box)
        self.db.commit()
        self.db.refresh(new_box)
        
        return new_box
    
    def get_boxes(self, company_id: int) -> List[Box]:
        """
        Get all boxes for a company.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            
        Returns:
            List of boxes
        """
        return self.db.query(Box).filter(
            Box.company_id == company_id
        ).all()
    
    def get_box(self, box_id: int, company_id: int) -> Box:
        """
        Get a single box with ownership verification.
        
        Args:
            box_id: Box ID
            company_id: Company ID for ownership verification
            
        Returns:
            Box object
            
        Raises:
            HTTPException: If box not found or doesn't belong to company
        """
        box = self.db.query(Box).filter(
            Box.id == box_id,
            Box.company_id == company_id
        ).first()
        
        if not box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Box not found"
            )
        
        return box
    
    def update_box(
        self,
        box_id: int,
        box_data: BoxUpdate,
        company_id: int
    ) -> Box:
        """
        Update a box with ownership verification.
        
        Args:
            box_id: Box ID
            box_data: Box update data
            company_id: Company ID for ownership verification
            
        Returns:
            Updated box
            
        Raises:
            HTTPException: If box not found or doesn't belong to company
        """
        box = self.get_box(box_id, company_id)
        
        # Update fields if provided
        update_data = box_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(box, field, value)
        
        self.db.commit()
        self.db.refresh(box)
        
        return box
    
    def delete_box(self, box_id: int, company_id: int) -> None:
        """
        Delete a box with ownership verification.
        
        Args:
            box_id: Box ID
            company_id: Company ID for ownership verification
            
        Raises:
            HTTPException: If box not found or doesn't belong to company
        """
        box = self.get_box(box_id, company_id)
        
        self.db.delete(box)
        self.db.commit()
    
    def track_usage(self, box_id: int, company_id: int) -> Box:
        """
        Increment usage count for a box.
        
        Args:
            box_id: Box ID
            company_id: Company ID for ownership verification
            
        Returns:
            Updated box with incremented usage count
            
        Raises:
            HTTPException: If box not found or doesn't belong to company
        """
        box = self.get_box(box_id, company_id)
        
        box.usage_count += 1
        
        self.db.commit()
        self.db.refresh(box)
        
        return box
