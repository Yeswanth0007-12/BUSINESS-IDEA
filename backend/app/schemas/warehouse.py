"""
Warehouse integration schemas for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Warehouse Optimization Schemas

class ItemDimensions(BaseModel):
    """Dimensions for a warehouse item."""
    length_cm: float = Field(..., gt=0, description="Length in centimeters")
    width_cm: float = Field(..., gt=0, description="Width in centimeters")
    height_cm: float = Field(..., gt=0, description="Height in centimeters")


class WarehouseItem(BaseModel):
    """Item in a warehouse optimization request."""
    sku: str = Field(..., min_length=1, max_length=100, description="Product SKU")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    dimensions: Optional[ItemDimensions] = Field(None, description="Item dimensions (optional if SKU exists)")
    weight_kg: Optional[float] = Field(None, gt=0, description="Item weight in kg (optional if SKU exists)")


class ShippingAddress(BaseModel):
    """Shipping address for rate calculation."""
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")


class WarehouseOptimizationRequest(BaseModel):
    """Request schema for warehouse optimization endpoint."""
    order_id: str = Field(..., min_length=1, max_length=100, description="External order ID")
    items: List[WarehouseItem] = Field(..., min_items=1, description="List of items to pack")
    shipping_address: Optional[ShippingAddress] = Field(None, description="Shipping address for rate calculation")
    courier_rate: Optional[float] = Field(2.5, gt=0, description="Courier rate per kg (default: 2.5)")
    
    class Config:
        schema_extra = {
            "example": {
                "order_id": "WH-12345",
                "items": [
                    {
                        "sku": "PROD-123",
                        "quantity": 2,
                        "dimensions": {
                            "length_cm": 30.0,
                            "width_cm": 20.0,
                            "height_cm": 10.0
                        },
                        "weight_kg": 2.5
                    }
                ],
                "shipping_address": {
                    "country": "US",
                    "postal_code": "12345"
                },
                "courier_rate": 2.5
            }
        }


class BoxDimensions(BaseModel):
    """Box dimensions in response."""
    length_cm: float
    width_cm: float
    height_cm: float


class PackedBox(BaseModel):
    """A packed box in the optimization result."""
    box_id: int
    box_name: str
    dimensions: BoxDimensions
    items: List[str] = Field(..., description="List of SKUs packed in this box")
    total_weight_kg: float
    space_utilization: float = Field(..., description="Space utilization percentage")
    box_cost: float
    shipping_cost: float
    total_cost: float


class WarehouseOptimizationResponse(BaseModel):
    """Response schema for warehouse optimization endpoint."""
    optimization_id: str = Field(..., description="Unique optimization ID")
    order_id: str = Field(..., description="External order ID from request")
    status: str = Field(..., description="Optimization status (success, partial, failed)")
    boxes_required: List[PackedBox] = Field(..., description="List of boxes required for packing")
    total_boxes: int = Field(..., description="Total number of boxes")
    total_cost: float = Field(..., description="Total cost (packaging + shipping)")
    estimated_shipping_cost: float = Field(..., description="Total estimated shipping cost")
    unpacked_items: Optional[List[str]] = Field(None, description="List of SKUs that couldn't be packed")
    
    class Config:
        schema_extra = {
            "example": {
                "optimization_id": "opt-789",
                "order_id": "WH-12345",
                "status": "success",
                "boxes_required": [
                    {
                        "box_id": 5,
                        "box_name": "Medium Box",
                        "dimensions": {
                            "length_cm": 40.0,
                            "width_cm": 30.0,
                            "height_cm": 20.0
                        },
                        "items": ["PROD-123", "PROD-123"],
                        "total_weight_kg": 5.0,
                        "space_utilization": 75.5,
                        "box_cost": 5.00,
                        "shipping_cost": 12.50,
                        "total_cost": 17.50
                    }
                ],
                "total_boxes": 1,
                "total_cost": 17.50,
                "estimated_shipping_cost": 12.50
            }
        }


# Webhook Schemas

class WebhookCreate(BaseModel):
    """Schema for creating a webhook."""
    url: str = Field(..., min_length=1, max_length=500, description="HTTPS webhook endpoint URL")
    events: List[str] = Field(..., min_items=1, description="List of event types to subscribe to")
    secret: str = Field(..., min_length=16, max_length=255, description="Secret for HMAC signature verification")
    
    @validator('url')
    def validate_https(cls, v):
        """Ensure webhook URL uses HTTPS."""
        if not v.startswith('https://'):
            raise ValueError('Webhook URL must use HTTPS protocol')
        return v
    
    @validator('events')
    def validate_events(cls, v):
        """Ensure event types are valid."""
        valid_events = ['optimization.completed', 'optimization.failed']
        for event in v:
            if event not in valid_events:
                raise ValueError(f'Invalid event type: {event}. Valid events: {valid_events}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://warehouse.example.com/webhooks/packoptima",
                "events": ["optimization.completed", "optimization.failed"],
                "secret": "webhook_secret_key_min_16_chars"
            }
        }


class WebhookResponse(BaseModel):
    """Schema for webhook response."""
    id: int
    company_id: int
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "company_id": 1,
                "url": "https://warehouse.example.com/webhooks/packoptima",
                "events": ["optimization.completed", "optimization.failed"],
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class WebhookPayload(BaseModel):
    """Schema for webhook event payload."""
    event: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    
    class Config:
        schema_extra = {
            "example": {
                "event": "optimization.completed",
                "timestamp": "2024-01-15T10:30:00Z",
                "data": {
                    "optimization_id": "opt-789",
                    "order_id": "WH-12345",
                    "status": "completed",
                    "result": {}
                }
            }
        }


# API Key Schemas

class ApiKeyCreate(BaseModel):
    """Schema for creating an API key."""
    name: str = Field(..., min_length=1, max_length=100, description="Descriptive name for the API key")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Production Warehouse System"
            }
        }


class ApiKeyResponse(BaseModel):
    """Schema for API key response (only shown once at creation)."""
    id: int
    name: str
    api_key: str = Field(..., description="API key (only shown once)")
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Production Warehouse System",
                "api_key": "pk_live_1234567890abcdef",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ApiKeyInfo(BaseModel):
    """Schema for API key information (without the actual key)."""
    id: int
    name: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Production Warehouse System",
                "created_at": "2024-01-15T10:30:00Z",
                "last_used_at": "2024-01-15T14:30:00Z",
                "is_active": True
            }
        }
