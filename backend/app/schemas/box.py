from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal


class BoxCreate(BaseModel):
    name: str = Field(..., min_length=1)
    length_cm: float = Field(..., gt=0)
    width_cm: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    cost_per_unit: float = Field(..., gt=0)
    max_weight_kg: float = Field(default=30.0, gt=0)
    material_type: Literal["cardboard", "plastic", "wood"] = Field(default="cardboard")
    
    @field_validator('length_cm', 'width_cm', 'height_cm', 'cost_per_unit', 'max_weight_kg')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Must be a positive number')
        return v


class BoxUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    length_cm: Optional[float] = Field(None, gt=0)
    width_cm: Optional[float] = Field(None, gt=0)
    height_cm: Optional[float] = Field(None, gt=0)
    cost_per_unit: Optional[float] = Field(None, gt=0)
    max_weight_kg: Optional[float] = Field(None, gt=0)
    material_type: Optional[Literal["cardboard", "plastic", "wood"]] = None


class BoxResponse(BaseModel):
    id: int
    company_id: int
    name: str
    length_cm: float
    width_cm: float
    height_cm: float
    cost_per_unit: float
    max_weight_kg: float
    material_type: str
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
