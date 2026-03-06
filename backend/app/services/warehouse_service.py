"""
Warehouse integration service for external warehouse systems.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
import uuid
import hmac
import hashlib
import httpx
import asyncio
from datetime import datetime

from app.models.product import Product
from app.models.box import Box
from app.models.webhook import Webhook, WebhookDelivery
from app.schemas.warehouse import (
    WarehouseOptimizationRequest,
    WarehouseOptimizationResponse,
    PackedBox,
    BoxDimensions,
    WebhookCreate,
    WebhookResponse,
    WebhookPayload
)
from app.services.optimization_engine import OptimizationEngine

logger = logging.getLogger(__name__)


class WarehouseService:
    """Service layer for warehouse integration operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.optimization_engine = OptimizationEngine(db)
    
    def optimize_package(
        self,
        company_id: int,
        request: WarehouseOptimizationRequest
    ) -> WarehouseOptimizationResponse:
        """
        Optimize packaging for a warehouse order.
        
        Args:
            company_id: Company ID from API key authentication
            request: Warehouse optimization request
            
        Returns:
            Warehouse optimization response with packed boxes
            
        Raises:
            HTTPException: If SKUs not found or no boxes available
        """
        # Generate unique optimization ID
        optimization_id = f"opt-{uuid.uuid4().hex[:12]}"
        
        # Prepare items for packing
        items_to_pack = []
        
        for item in request.items:
            # Look up product by SKU
            product = self.db.query(Product).filter(
                Product.company_id == company_id,
                Product.sku == item.sku
            ).first()
            
            if not product:
                # If product doesn't exist and dimensions/weight provided, create temporary product
                if item.dimensions and item.weight_kg:
                    # Create a temporary product object (not saved to DB)
                    from app.models.product import Product as ProductModel
                    product = ProductModel(
                        company_id=company_id,
                        sku=item.sku,
                        name=item.sku,
                        category="general",
                        length_cm=item.dimensions.length_cm,
                        width_cm=item.dimensions.width_cm,
                        height_cm=item.dimensions.height_cm,
                        weight_kg=item.weight_kg,
                        fragile=False,
                        stackable=True
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product SKU '{item.sku}' not found. Provide dimensions and weight for unknown SKUs."
                    )
            
            # Add to packing list with quantity
            items_to_pack.append({
                'product': product,
                'quantity': item.quantity
            })
        
        # Get available boxes
        boxes = self.db.query(Box).filter(Box.company_id == company_id).all()
        
        if not boxes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No boxes found. Please add boxes to your account first."
            )
        
        # Run bin packing algorithm
        courier_rate = request.courier_rate or 2.5
        packing_result = self.optimization_engine.pack_multi_product_order(
            items_to_pack,
            boxes,
            courier_rate
        )
        
        # Build response
        packed_boxes = []
        total_shipping_cost = 0.0
        
        for idx, box_state in enumerate(packing_result['boxes_used'], 1):
            box = box_state['box']
            
            # Get SKUs of packed products
            packed_skus = [p.sku for p in box_state['products_packed']]
            
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
            total_shipping_cost += shipping_cost
            
            packed_box = PackedBox(
                box_id=box.id,
                box_name=box.name,
                dimensions=BoxDimensions(
                    length_cm=box.length_cm,
                    width_cm=box.width_cm,
                    height_cm=box.height_cm
                ),
                items=packed_skus,
                total_weight_kg=round(box_state['current_weight'], 2),
                space_utilization=round(space_utilization, 2),
                box_cost=round(box.cost_per_unit, 2),
                shipping_cost=round(shipping_cost, 2),
                total_cost=round(box.cost_per_unit + shipping_cost, 2)
            )
            packed_boxes.append(packed_box)
        
        # Determine status
        if packing_result['success']:
            response_status = "success"
            unpacked_items = None
        else:
            response_status = "partial"
            unpacked_items = [p.sku for p in packing_result['unpacked_items']]
        
        logger.info(
            f"Warehouse optimization {optimization_id} for order {request.order_id}: "
            f"{packing_result['total_boxes']} boxes, status={response_status}"
        )
        
        return WarehouseOptimizationResponse(
            optimization_id=optimization_id,
            order_id=request.order_id,
            status=response_status,
            boxes_required=packed_boxes,
            total_boxes=packing_result['total_boxes'],
            total_cost=round(packing_result['total_cost'], 2),
            estimated_shipping_cost=round(total_shipping_cost, 2),
            unpacked_items=unpacked_items
        )

    
    # Webhook Management Methods
    
    def register_webhook(
        self,
        company_id: int,
        webhook_data: WebhookCreate
    ) -> Webhook:
        """
        Register a new webhook for event notifications.
        
        Args:
            company_id: Company ID from API key authentication
            webhook_data: Webhook registration data
            
        Returns:
            Created webhook
            
        Raises:
            HTTPException: If webhook URL is invalid
        """
        # Validate URL is HTTPS (already validated by schema, but double-check)
        if not webhook_data.url.startswith('https://'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook URL must use HTTPS protocol"
            )
        
        # Create webhook
        webhook = Webhook(
            company_id=company_id,
            url=webhook_data.url,
            events=webhook_data.events,
            secret=webhook_data.secret,
            is_active=True
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        
        logger.info(f"Registered webhook {webhook.id} for company {company_id}")
        
        return webhook
    
    def list_webhooks(self, company_id: int) -> List[Webhook]:
        """
        List all webhooks for a company.
        
        Args:
            company_id: Company ID
            
        Returns:
            List of webhooks
        """
        return self.db.query(Webhook).filter(
            Webhook.company_id == company_id
        ).all()
    
    def get_webhook(self, company_id: int, webhook_id: int) -> Optional[Webhook]:
        """
        Get a webhook by ID with company filtering.
        
        Args:
            company_id: Company ID
            webhook_id: Webhook ID
            
        Returns:
            Webhook or None
        """
        return self.db.query(Webhook).filter(
            Webhook.id == webhook_id,
            Webhook.company_id == company_id
        ).first()
    
    def delete_webhook(self, company_id: int, webhook_id: int) -> bool:
        """
        Delete a webhook.
        
        Args:
            company_id: Company ID
            webhook_id: Webhook ID
            
        Returns:
            True if deleted, False if not found
        """
        webhook = self.get_webhook(company_id, webhook_id)
        if not webhook:
            return False
        
        self.db.delete(webhook)
        self.db.commit()
        
        logger.info(f"Deleted webhook {webhook_id} for company {company_id}")
        
        return True
    
    def generate_webhook_signature(self, payload: str, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.
        
        Args:
            payload: JSON payload as string
            secret: Webhook secret
            
        Returns:
            Hex-encoded HMAC signature
        """
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    async def deliver_webhook(
        self,
        webhook: Webhook,
        event: str,
        data: Dict[str, Any],
        max_retries: int = 3
    ) -> bool:
        """
        Deliver a webhook event with retry logic.
        
        Args:
            webhook: Webhook object
            event: Event type
            data: Event data
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if delivery successful, False otherwise
        """
        # Create payload
        payload_obj = WebhookPayload(
            event=event,
            timestamp=datetime.utcnow(),
            data=data
        )
        payload_json = payload_obj.json()
        
        # Generate signature
        signature = self.generate_webhook_signature(payload_json, webhook.secret)
        
        # Create delivery record
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event=event,
            payload=data,
            status="pending",
            retry_count=0
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        
        # Attempt delivery with retries
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        webhook.url,
                        content=payload_json,
                        headers={
                            "Content-Type": "application/json",
                            "X-PackOptima-Signature": signature,
                            "X-PackOptima-Event": event
                        }
                    )
                    
                    # Update delivery record
                    delivery.response_code = response.status_code
                    delivery.response_body = response.text[:1000]  # Limit to 1000 chars
                    delivery.delivered_at = datetime.utcnow()
                    delivery.retry_count = attempt + 1
                    
                    if response.status_code < 300:
                        # Success
                        delivery.status = "success"
                        self.db.commit()
                        logger.info(f"Webhook {webhook.id} delivered successfully")
                        return True
                    else:
                        # HTTP error
                        logger.warning(
                            f"Webhook {webhook.id} delivery failed with status {response.status_code}"
                        )
                        
            except Exception as e:
                logger.error(f"Webhook {webhook.id} delivery error: {e}")
                delivery.response_body = str(e)[:1000]
                delivery.retry_count = attempt + 1
            
            # Exponential backoff before retry
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
        
        # All retries failed
        delivery.status = "failed"
        self.db.commit()
        
        # Deactivate webhook after repeated failures
        failed_deliveries = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook.id,
            WebhookDelivery.status == "failed"
        ).count()
        
        if failed_deliveries >= 10:
            webhook.is_active = False
            self.db.commit()
            logger.warning(f"Webhook {webhook.id} deactivated after {failed_deliveries} failures")
        
        return False
    
    async def trigger_webhook_event(
        self,
        company_id: int,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Trigger webhook event for all subscribed webhooks.
        
        Args:
            company_id: Company ID
            event: Event type (e.g., "optimization.completed")
            data: Event data
        """
        # Get all active webhooks subscribed to this event
        webhooks = self.db.query(Webhook).filter(
            Webhook.company_id == company_id,
            Webhook.is_active == True
        ).all()
        
        # Filter webhooks subscribed to this event
        subscribed_webhooks = [
            wh for wh in webhooks
            if event in wh.events
        ]
        
        # Deliver to all subscribed webhooks
        for webhook in subscribed_webhooks:
            try:
                await self.deliver_webhook(webhook, event, data)
            except Exception as e:
                logger.error(f"Error delivering webhook {webhook.id}: {e}")
