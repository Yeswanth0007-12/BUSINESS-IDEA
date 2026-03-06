from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.order import Order, OrderItem, OrderPackingResult
from app.models.product import Product
from app.models.box import Box
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderPackingSummary, OrderPackingResultResponse
from app.services.optimization_engine import OptimizationEngine

logger = logging.getLogger(__name__)


class OrderService:
    """Service layer for order management and packing optimization"""
    
    def __init__(self, db: Session):
        self.db = db
        self.optimization_engine = OptimizationEngine(db)
    
    def create_order(self, company_id: int, order_data: OrderCreate) -> Order:
        """
        Create a new order with items.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            order_data: Order creation data
            
        Returns:
            Created order
            
        Raises:
            HTTPException: If order_number already exists or products not found
        """
        # Check if order_number already exists for this company
        existing = self.db.query(Order).filter(
            Order.company_id == company_id,
            Order.order_number == order_data.order_number
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order number '{order_data.order_number}' already exists"
            )
        
        # Validate all products exist and belong to company
        for item in order_data.items:
            product = self.db.query(Product).filter(
                Product.id == item.product_id,
                Product.company_id == company_id
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product ID {item.product_id} not found"
                )
        
        # Create order
        order = Order(
            company_id=company_id,
            order_number=order_data.order_number,
            customer_name=order_data.customer_name,
            status="pending"
        )
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Create order items
        for item in order_data.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"Created order {order.order_number} with {len(order_data.items)} items")
        
        return order
    
    def get_order(self, company_id: int, order_id: int) -> Optional[Order]:
        """
        Get order by ID with company filtering.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            order_id: Order ID
            
        Returns:
            Order or None
        """
        return self.db.query(Order).filter(
            Order.id == order_id,
            Order.company_id == company_id
        ).first()
    
    def list_orders(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Order]:
        """
        List orders with pagination and optional status filtering.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of orders
        """
        query = self.db.query(Order).filter(Order.company_id == company_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def optimize_order_packing(
        self,
        company_id: int,
        order_id: int,
        courier_rate: float = 2.5
    ) -> OrderPackingSummary:
        """
        Optimize packing for an order using bin packing algorithm.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            order_id: Order ID
            courier_rate: Shipping cost per kg
            
        Returns:
            Order packing summary
            
        Raises:
            HTTPException: If order not found or no boxes available
        """
        # Get order with items
        order = self.get_order(company_id, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order ID {order_id} not found"
            )
        
        # Get order items with products
        order_items = self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        if not order_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has no items"
            )
        
        # Prepare order items for packing
        items_to_pack = []
        for item in order_items:
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                items_to_pack.append({
                    'product': product,
                    'quantity': item.quantity
                })
        
        # Get available boxes
        boxes = self.db.query(Box).filter(Box.company_id == company_id).all()
        
        if not boxes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No boxes found. Please add boxes first."
            )
        
        # Update order status
        order.status = "processing"
        self.db.commit()
        
        # Run bin packing algorithm
        packing_result = self.optimization_engine.pack_multi_product_order(
            items_to_pack,
            boxes,
            courier_rate
        )
        
        # Clear existing packing results
        self.db.query(OrderPackingResult).filter(
            OrderPackingResult.order_id == order_id
        ).delete()
        
        # Save packing results
        packing_responses = []
        for idx, box_state in enumerate(packing_result['boxes_used'], 1):
            box = box_state['box']
            products_packed = [
                {'product_id': p.id, 'product_name': p.name}
                for p in box_state['products_packed']
            ]
            
            # Calculate space utilization for this box
            box_volume = box.length_cm * box.width_cm * box.height_cm
            used_volume = box_volume - box_state['remaining_space']
            space_utilization = (used_volume / box_volume) * 100 if box_volume > 0 else 0
            
            # Calculate shipping cost for this box
            vol_weight = self.optimization_engine.calculate_volumetric_weight(
                box.length_cm, box.width_cm, box.height_cm
            )
            billable_weight = self.optimization_engine.calculate_billable_weight(
                box_state['current_weight'], vol_weight
            )
            shipping_cost = billable_weight * courier_rate
            
            packing_result_record = OrderPackingResult(
                order_id=order_id,
                box_id=box.id,
                box_number=idx,
                products_packed=products_packed,
                total_weight=box_state['current_weight'],
                space_utilization=space_utilization,
                shipping_cost=shipping_cost
            )
            self.db.add(packing_result_record)
            self.db.flush()
            
            packing_responses.append(OrderPackingResultResponse(
                id=packing_result_record.id,
                order_id=order_id,
                box_id=box.id,
                box_number=idx,
                products_packed=products_packed,
                total_weight=box_state['current_weight'],
                space_utilization=space_utilization,
                shipping_cost=shipping_cost
            ))
        
        # Update order status
        if packing_result['success']:
            order.status = "completed"
            message = f"Successfully packed all items into {packing_result['total_boxes']} boxes"
        else:
            order.status = "failed"
            message = f"Could not pack {len(packing_result['unpacked_items'])} items"
        
        self.db.commit()
        
        # Prepare unpacked items info
        unpacked_info = [
            {'product_id': p.id, 'product_name': p.name}
            for p in packing_result['unpacked_items']
        ]
        
        return OrderPackingSummary(
            order_id=order_id,
            order_number=order.order_number,
            total_boxes=packing_result['total_boxes'],
            total_cost=packing_result['total_cost'],
            total_shipping_cost=packing_result['total_shipping_cost'],
            success=packing_result['success'],
            packing_results=packing_responses,
            unpacked_items=unpacked_info,
            message=message
        )
