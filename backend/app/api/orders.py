from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderPackingSummary
)
from app.services.order_service import OrderService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order with multiple items.
    
    Requires authentication. Order is created for the current user's company.
    """
    order_service = OrderService(db)
    order = order_service.create_order(current_user.company_id, order_data)
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by ID.
    
    Requires authentication. Only returns orders belonging to the current user's company.
    """
    order_service = OrderService(db)
    order = order_service.get_order(current_user.company_id, order_id)
    
    if not order:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order ID {order_id} not found"
        )
    
    return order


@router.get("", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List orders with pagination.
    
    Requires authentication. Only returns orders belonging to the current user's company.
    
    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Optional status filter (pending, processing, completed, failed)
    """
    order_service = OrderService(db)
    orders = order_service.list_orders(
        current_user.company_id,
        skip=skip,
        limit=limit,
        status=status_filter
    )
    return orders


@router.post("/{order_id}/optimize", response_model=OrderPackingSummary)
def optimize_order_packing(
    order_id: int,
    courier_rate: float = Query(2.5, gt=0, description="Shipping cost per kg"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Optimize packing for an order using bin packing algorithm.
    
    Requires authentication. Only optimizes orders belonging to the current user's company.
    
    The algorithm:
    1. Sorts products by volume (largest first)
    2. Uses First Fit Decreasing to pack products into boxes
    3. Respects fragile and stackability constraints
    4. Calculates shipping costs based on billable weight
    
    Query parameters:
    - courier_rate: Shipping cost per kg (default: 2.5)
    """
    order_service = OrderService(db)
    return order_service.optimize_order_packing(
        current_user.company_id,
        order_id,
        courier_rate
    )
