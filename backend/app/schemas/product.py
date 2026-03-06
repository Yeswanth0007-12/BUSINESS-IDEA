from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    length_cm: float = Field(..., gt=0)
    width_cm: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    current_box_id: Optional[int] = None
    monthly_order_volume: int = Field(..., ge=0)
    fragile: bool = False
    stackable: bool = True
    
    @field_validator('length_cm', 'width_cm', 'height_cm', 'weight_kg')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Must be a positive number')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1)
    length_cm: Optional[float] = Field(None, gt=0)
    width_cm: Optional[float] = Field(None, gt=0)
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    current_box_id: Optional[int] = None
    monthly_order_volume: Optional[int] = Field(None, ge=0)
    fragile: Optional[bool] = None
    stackable: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    company_id: int
    name: str
    sku: str
    category: str
    length_cm: float
    width_cm: float
    height_cm: float
    weight_kg: float
    current_box_id: Optional[int]
    monthly_order_volume: int
    fragile: bool
    stackable: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
