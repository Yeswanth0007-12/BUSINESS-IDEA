from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.product import Product
from app.models.box import Box
from app.models.optimization_run import OptimizationRun
from app.models.optimization_result import OptimizationResult as OptimizationResultModel
from app.schemas.optimization import OptimizationRequest, OptimizationResult, OptimizationSummary

# Configure logging
logger = logging.getLogger(__name__)


class OptimizationEngine:
    """
    Core optimization engine for packaging recommendations.
    Implements deterministic algorithms for box selection and cost savings.
    
    Enhanced with:
    - 6-orientation testing for optimal product placement
    - Weight constraint validation
    - Shipping cost calculation (volumetric + billable weight)
    - Space utilization metrics
    """
    
    # Category padding constants (in cm)
    CATEGORY_PADDING = {
        "electronics": 3.0,
        "fragile": 4.0,
        "clothing": 1.0,
        "books": 1.5,
        "toys": 2.0,
    }
    DEFAULT_PADDING = 2.0
    
    # Volumetric weight divisor
    VOLUMETRIC_DIVISOR = 5000
    
    # Default courier rate (per kg)
    DEFAULT_COURIER_RATE = 2.5
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_volumetric_weight(self, length_cm: float, width_cm: float, height_cm: float) -> float:
        """
        Calculate volumetric weight using the formula: (L × W × H) / 5000
        
        Args:
            length_cm: Length in centimeters
            width_cm: Width in centimeters
            height_cm: Height in centimeters
            
        Returns:
            Volumetric weight in kg
        """
        return round((length_cm * width_cm * height_cm) / self.VOLUMETRIC_DIVISOR, 2)
    
    def calculate_billable_weight(self, actual_weight_kg: float, volumetric_weight_kg: float) -> float:
        """
        Calculate billable weight as max(actual_weight, volumetric_weight).
        
        Args:
            actual_weight_kg: Physical weight in kg
            volumetric_weight_kg: Calculated volumetric weight in kg
            
        Returns:
            Billable weight in kg
        """
        return max(actual_weight_kg, volumetric_weight_kg)
    
    def calculate_shipping_cost(self, box: Box, product_weight_kg: float, courier_rate: float = None) -> float:
        """
        Calculate shipping cost based on billable weight.
        
        Args:
            box: Box object with dimensions
            product_weight_kg: Product weight in kg
            courier_rate: Cost per kg (default: 2.5)
            
        Returns:
            Shipping cost
        """
        if courier_rate is None:
            courier_rate = self.DEFAULT_COURIER_RATE
            
        volumetric_weight = self.calculate_volumetric_weight(
            box.length_cm, box.width_cm, box.height_cm
        )
        billable_weight = self.calculate_billable_weight(product_weight_kg, volumetric_weight)
        shipping_cost = billable_weight * courier_rate
        
        return round(shipping_cost, 2)
    
    def validate_weight_constraint(self, product_weight_kg: float, box_max_weight_kg: float) -> bool:
        """
        Validate that product weight does not exceed box maximum weight.
        
        Args:
            product_weight_kg: Product weight in kg
            box_max_weight_kg: Box maximum weight capacity in kg
            
        Returns:
            True if weight constraint is satisfied
        """
        return product_weight_kg <= box_max_weight_kg
    
    def test_all_orientations(
        self,
        product_dims: Tuple[float, float, float],
        box_dims: Tuple[float, float, float],
        padding: float
    ) -> Tuple[Optional[Tuple[float, float, float]], float]:
        """
        Test all 6 possible orientations of a product to find best fit.
        
        Args:
            product_dims: (length, width, height) in cm
            box_dims: (box_length, box_width, box_height) in cm
            padding: Padding requirement in cm
            
        Returns:
            Tuple of (best_orientation or None, space_utilization percentage)
        """
        length, width, height = product_dims
        box_l, box_w, box_h = box_dims
        
        # Generate all 6 orientations
        orientations = [
            (length, width, height),
            (length, height, width),
            (width, length, height),
            (width, height, length),
            (height, length, width),
            (height, width, length)
        ]
        
        best_orientation = None
        best_utilization = 0.0
        
        # Calculate box volume once
        box_volume = box_l * box_w * box_h
        
        for orientation in orientations:
            # Add padding to each dimension
            required_l = orientation[0] + (2 * padding)
            required_w = orientation[1] + (2 * padding)
            required_h = orientation[2] + (2 * padding)
            
            # Check if fits in box
            if required_l <= box_l and required_w <= box_w and required_h <= box_h:
                # Calculate space utilization
                product_volume = orientation[0] * orientation[1] * orientation[2]
                utilization = (product_volume / box_volume) * 100
                
                # Keep best utilization
                if utilization > best_utilization:
                    best_orientation = orientation
                    best_utilization = utilization
        
        return best_orientation, round(best_utilization, 2)
    
    def get_category_padding(self, category: str) -> float:
        """
        Get padding requirement for a product category.
        
        Args:
            category: Product category (lowercase)
            
        Returns:
            Padding in centimeters
        """
        category_lower = category.lower()
        return self.CATEGORY_PADDING.get(category_lower, self.DEFAULT_PADDING)
    
    def find_optimal_box(
        self,
        product: Product,
        available_boxes: List[Box],
        padding: float
    ) -> Dict[str, Any]:
        """
        Find the optimal box for a product using 6-orientation testing and weight constraints.
        
        Args:
            product: Product to optimize
            available_boxes: List of available boxes
            padding: Required padding in cm
            
        Returns:
            Dictionary with box, orientation, space_utilization, unused_volume, and reason
        """
        product_dims = (product.length_cm, product.width_cm, product.height_cm)
        
        logger.info(f"Product '{product.name}' dimensions: L={product.length_cm:.2f}, W={product.width_cm:.2f}, H={product.height_cm:.2f}, Weight={product.weight_kg:.2f}kg")
        
        # Filter boxes by weight constraint first
        suitable_boxes = []
        
        for box in available_boxes:
            # Check weight constraint
            if not self.validate_weight_constraint(product.weight_kg, box.max_weight_kg):
                logger.debug(f"  Box '{box.name}' rejected: weight {product.weight_kg}kg exceeds max {box.max_weight_kg}kg")
                continue
            
            # Test all orientations
            box_dims = (box.length_cm, box.width_cm, box.height_cm)
            orientation, utilization = self.test_all_orientations(product_dims, box_dims, padding)
            
            if orientation is not None:
                # Calculate volumes
                product_volume = orientation[0] * orientation[1] * orientation[2]
                box_volume = box.length_cm * box.width_cm * box.height_cm
                unused_volume = box_volume - product_volume
                
                suitable_boxes.append({
                    'box': box,
                    'orientation': orientation,
                    'utilization': utilization,
                    'unused_volume': unused_volume
                })
                logger.debug(f"  Box '{box.name}' fits: utilization={utilization:.1f}%, cost=${box.cost_per_unit}")
        
        if not suitable_boxes:
            reason = f"No suitable box found (weight or dimensions)"
            logger.warning(f"  {reason}")
            return {
                'box': None,
                'orientation': None,
                'space_utilization': 0.0,
                'unused_volume': 0.0,
                'reason': reason
            }
        
        # Select box with minimum cost (primary) and best utilization (secondary)
        optimal = min(suitable_boxes, key=lambda x: (x['box'].cost_per_unit, -x['utilization']))
        
        logger.info(f"  Optimal box selected: '{optimal['box'].name}' at ${optimal['box'].cost_per_unit}, utilization={optimal['utilization']:.1f}%")
        
        return {
            'box': optimal['box'],
            'orientation': optimal['orientation'],
            'space_utilization': optimal['utilization'],
            'unused_volume': round(optimal['unused_volume'], 2),
            'reason': "Success"
        }
    
    def calculate_savings(
        self,
        current_box: Box,
        recommended_box: Box,
        monthly_volume: int
    ) -> Tuple[float, float]:
        """
        Calculate monthly and annual savings.
        
        Args:
            current_box: Current box being used
            recommended_box: Recommended optimal box
            monthly_volume: Monthly order volume
            
        Returns:
            Tuple of (monthly_savings, annual_savings)
        """
        cost_difference = current_box.cost_per_unit - recommended_box.cost_per_unit
        monthly_savings = cost_difference * monthly_volume
        annual_savings = monthly_savings * 12
        
        return monthly_savings, annual_savings
    
    def optimize_packaging(
        self,
        company_id: int,
        request: OptimizationRequest,
        courier_rate: float = None
    ) -> OptimizationSummary:
        """
        Main optimization algorithm that analyzes products and recommends optimal boxes.
        
        FIXED: Now handles products without current_box_id assigned.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            request: Optimization request with optional product IDs
            
        Returns:
            Optimization summary with results, savings, and debug info
            
        Raises:
            HTTPException: If no products or boxes found
        """
        logger.info(f"=== Starting Optimization for Company {company_id} ===")
        
        # STEP 1: Fetch products with company filtering
        query = self.db.query(Product).filter(Product.company_id == company_id)
        
        if request.product_ids:
            query = query.filter(Product.id.in_(request.product_ids))
        
        products = query.all()
        products_loaded = len(products)
        
        logger.info(f"STEP 1: Products loaded: {products_loaded}")
        
        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No products found for optimization"
            )
        
        # STEP 2: Fetch available boxes with company filtering
        boxes = self.db.query(Box).filter(Box.company_id == company_id).all()
        boxes_loaded = len(boxes)
        
        logger.info(f"STEP 2: Boxes loaded: {boxes_loaded}")
        
        if not boxes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No boxes found. Please add boxes first."
            )
        
        # Create optimization run record
        optimization_run = OptimizationRun(
            company_id=company_id,
            products_analyzed=0,
            total_monthly_savings=0.0,
            total_annual_savings=0.0
        )
        self.db.add(optimization_run)
        self.db.flush()  # Get run ID
        
        # STEP 3: Process each product
        results = []
        total_monthly_savings = 0.0
        products_with_savings = 0
        products_with_fit_boxes = 0
        products_without_current_box = 0
        products_skipped = []
        
        logger.info(f"STEP 3: Processing {products_loaded} products...")
        
        for product in products:
            logger.info(f"\nAnalyzing Product: '{product.name}' (ID: {product.id})")
            logger.info(f"  Dimensions: L={product.length_cm}, W={product.width_cm}, H={product.height_cm}")
            logger.info(f"  Monthly Volume: {product.monthly_order_volume}")
            logger.info(f"  Current Box ID: {product.current_box_id}")
            
            # Get category padding
            padding = self.get_category_padding(product.category)
            logger.info(f"  Category '{product.category}' padding: {padding} cm")
            
            # Find optimal box (returns dict with box, orientation, utilization, etc.)
            optimal_result = self.find_optimal_box(product, boxes, padding)
            optimal_box = optimal_result['box']
            
            if not optimal_box:
                logger.warning(f"  ❌ No suitable box found: {optimal_result['reason']}")
                products_skipped.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "reason": optimal_result['reason']
                })
                continue
            
            products_with_fit_boxes += 1
            
            # CRITICAL FIX: Handle products WITHOUT current_box_id
            # Auto-assign an oversized box as baseline for comparison
            if not product.current_box_id:
                products_without_current_box += 1
                logger.info(f"  ℹ️  Product has no current box assigned - auto-assigning baseline")
                
                # Find a suitable oversized box (upper 50-75% by cost) as baseline
                # This simulates real-world inefficiency where products are in oversized boxes
                suitable_baseline_boxes = []
                for box in boxes:
                    if self.validate_weight_constraint(product.weight_kg, box.max_weight_kg):
                        box_dims = (box.length_cm, box.width_cm, box.height_cm)
                        product_dims = (product.length_cm, product.width_cm, product.height_cm)
                        orientation, utilization = self.test_all_orientations(product_dims, box_dims, padding)
                        if orientation is not None:
                            suitable_baseline_boxes.append((box, utilization))
                
                if suitable_baseline_boxes:
                    # Sort by cost (descending) and pick from upper 50-75% range
                    suitable_baseline_boxes.sort(key=lambda x: x[0].cost_per_unit, reverse=True)
                    upper_range_start = len(suitable_baseline_boxes) // 2
                    upper_range_end = int(len(suitable_baseline_boxes) * 0.75)
                    if upper_range_end <= upper_range_start:
                        upper_range_end = len(suitable_baseline_boxes)
                    
                    # Pick middle box from upper range
                    baseline_idx = (upper_range_start + upper_range_end) // 2
                    baseline_box = suitable_baseline_boxes[baseline_idx][0]
                    
                    # Auto-assign this box to the product
                    product.current_box_id = baseline_box.id
                    self.db.flush()
                    
                    logger.info(f"  🔧 Auto-assigned baseline box: '{baseline_box.name}' at ${baseline_box.cost_per_unit}")
                    
                    # Now proceed with normal comparison logic
                    current_box = baseline_box
                else:
                    # No suitable baseline found, show recommendation without savings
                    logger.info(f"  ⚠️  No suitable baseline box found for auto-assignment")
                    
                    # Calculate costs for new assignment
                    recommended_cost = optimal_box.cost_per_unit * product.monthly_order_volume
                
                    # For products without current box, we show the recommendation
                    # but savings are 0 (no comparison possible)
                    vol_weight_recommended = self.calculate_volumetric_weight(
                        optimal_box.length_cm,
                        optimal_box.width_cm,
                        optimal_box.height_cm
                    )
                    
                    # Phase 3: Calculate shipping costs
                    billable_weight_recommended = self.calculate_billable_weight(
                        product.weight_kg, vol_weight_recommended
                    )
                    shipping_cost_recommended = billable_weight_recommended * courier_rate
                    total_cost_recommended = (optimal_box.cost_per_unit + shipping_cost_recommended) * product.monthly_order_volume
                    
                    # Create result record (no savings, just recommendation)
                    result_record = OptimizationResultModel(
                        run_id=optimization_run.id,
                        product_id=product.id,
                        current_box_id=None,  # No current box
                        recommended_box_id=optimal_box.id,
                        current_cost=0.0,  # No current cost
                        recommended_cost=recommended_cost,
                        savings=0.0,  # No savings (no comparison)
                        savings_percentage=0.0,
                        volumetric_weight_current=0.0,
                        volumetric_weight_recommended=vol_weight_recommended,
                        # Phase 2 fields
                        orientation_length=optimal_result['orientation'][0] if optimal_result['orientation'] else None,
                        orientation_width=optimal_result['orientation'][1] if optimal_result['orientation'] else None,
                        orientation_height=optimal_result['orientation'][2] if optimal_result['orientation'] else None,
                        space_utilization=optimal_result['space_utilization'],
                        unused_volume=optimal_result['unused_volume'],
                        # Phase 3 fields
                        shipping_cost_current=0.0,
                        shipping_cost_recommended=shipping_cost_recommended * product.monthly_order_volume,
                        total_cost_current=0.0,
                        total_cost_recommended=total_cost_recommended,
                        billable_weight_current=0.0,
                        billable_weight_recommended=billable_weight_recommended
                    )
                    self.db.add(result_record)
                    
                    # Add to results list
                    results.append(OptimizationResult(
                        product_id=product.id,
                        product_name=product.name,
                        current_box_id=0,  # Indicate no current box
                        current_box_name="No box assigned",
                        current_cost=0.0,
                        recommended_box_id=optimal_box.id,
                        recommended_box_name=optimal_box.name,
                        recommended_cost=recommended_cost,
                        savings=0.0,
                        savings_percentage=0.0,
                        volumetric_weight_current=0.0,
                        volumetric_weight_recommended=vol_weight_recommended,
                        # Phase 2 fields
                        orientation=optimal_result['orientation'],
                        space_utilization=optimal_result['space_utilization'],
                        unused_volume=optimal_result['unused_volume'],
                        # Phase 3 fields
                        shipping_cost_current=0.0,
                        shipping_cost_recommended=shipping_cost_recommended * product.monthly_order_volume,
                        total_cost_current=0.0,
                        total_cost_recommended=total_cost_recommended,
                        billable_weight_current=0.0,
                        billable_weight_recommended=billable_weight_recommended
                    ))
                    
                    logger.info(f"  ✅ Recommendation: '{optimal_box.name}' at ${recommended_cost:.2f}/month (shipping: ${shipping_cost_recommended:.2f})")
                    continue
            
            # Handle products WITH current_box_id (comparison mode)
            current_box = self.db.query(Box).filter(Box.id == product.current_box_id).first()
            if not current_box:
                logger.warning(f"  ⚠️  Current box ID {product.current_box_id} not found")
                continue
            
            logger.info(f"  Current Box: '{current_box.name}' at ${current_box.cost_per_unit}")
            
            # Calculate volumetric weights
            vol_weight_current = self.calculate_volumetric_weight(
                current_box.length_cm,
                current_box.width_cm,
                current_box.height_cm
            )
            
            vol_weight_recommended = self.calculate_volumetric_weight(
                optimal_box.length_cm,
                optimal_box.width_cm,
                optimal_box.height_cm
            )
            
            # Phase 3: Calculate billable weights and shipping costs
            billable_weight_current = self.calculate_billable_weight(
                product.weight_kg, vol_weight_current
            )
            billable_weight_recommended = self.calculate_billable_weight(
                product.weight_kg, vol_weight_recommended
            )
            
            shipping_cost_current = billable_weight_current * courier_rate
            shipping_cost_recommended = billable_weight_recommended * courier_rate
            
            # Calculate costs and savings using monthly_order_volume
            # Box cost only (for backward compatibility)
            current_cost = current_box.cost_per_unit * product.monthly_order_volume
            recommended_cost = optimal_box.cost_per_unit * product.monthly_order_volume
            
            # Total cost (box + shipping)
            total_cost_current = (current_box.cost_per_unit + shipping_cost_current) * product.monthly_order_volume
            total_cost_recommended = (optimal_box.cost_per_unit + shipping_cost_recommended) * product.monthly_order_volume
            
            # Savings based on total cost (box + shipping)
            monthly_savings = total_cost_current - total_cost_recommended
            
            logger.info(f"  Current Cost: ${current_cost:.2f}/month (box) + ${shipping_cost_current * product.monthly_order_volume:.2f}/month (shipping) = ${total_cost_current:.2f}/month")
            logger.info(f"  Recommended Cost: ${recommended_cost:.2f}/month (box) + ${shipping_cost_recommended * product.monthly_order_volume:.2f}/month (shipping) = ${total_cost_recommended:.2f}/month")
            logger.info(f"  Monthly Savings: ${monthly_savings:.2f}")
            
            # Include ALL results (even if savings are 0 or negative)
            # This shows users their current packaging is already optimal
            savings_percentage = (monthly_savings / current_cost) * 100 if current_cost > 0 else 0
            
            # Create result record
            result_record = OptimizationResultModel(
                run_id=optimization_run.id,
                product_id=product.id,
                current_box_id=current_box.id,
                recommended_box_id=optimal_box.id,
                current_cost=current_cost,
                recommended_cost=recommended_cost,
                savings=monthly_savings,
                savings_percentage=savings_percentage,
                volumetric_weight_current=vol_weight_current,
                volumetric_weight_recommended=vol_weight_recommended,
                # Phase 2 fields
                orientation_length=optimal_result['orientation'][0] if optimal_result['orientation'] else None,
                orientation_width=optimal_result['orientation'][1] if optimal_result['orientation'] else None,
                orientation_height=optimal_result['orientation'][2] if optimal_result['orientation'] else None,
                space_utilization=optimal_result['space_utilization'],
                unused_volume=optimal_result['unused_volume'],
                # Phase 3 fields
                shipping_cost_current=shipping_cost_current * product.monthly_order_volume,
                shipping_cost_recommended=shipping_cost_recommended * product.monthly_order_volume,
                total_cost_current=total_cost_current,
                total_cost_recommended=total_cost_recommended,
                billable_weight_current=billable_weight_current,
                billable_weight_recommended=billable_weight_recommended
            )
            self.db.add(result_record)
            
            # Add to results list
            results.append(OptimizationResult(
                product_id=product.id,
                product_name=product.name,
                current_box_id=current_box.id,
                current_box_name=current_box.name,
                current_cost=current_cost,
                recommended_box_id=optimal_box.id,
                recommended_box_name=optimal_box.name,
                recommended_cost=recommended_cost,
                savings=monthly_savings,
                savings_percentage=savings_percentage,
                volumetric_weight_current=vol_weight_current,
                volumetric_weight_recommended=vol_weight_recommended,
                # Phase 2 fields
                orientation=optimal_result['orientation'],
                space_utilization=optimal_result['space_utilization'],
                unused_volume=optimal_result['unused_volume'],
                # Phase 3 fields
                shipping_cost_current=shipping_cost_current * product.monthly_order_volume,
                shipping_cost_recommended=shipping_cost_recommended * product.monthly_order_volume,
                total_cost_current=total_cost_current,
                total_cost_recommended=total_cost_recommended,
                billable_weight_current=billable_weight_current,
                billable_weight_recommended=billable_weight_recommended
            ))
            
            if monthly_savings > 0:
                total_monthly_savings += monthly_savings
                products_with_savings += 1
                logger.info(f"  ✅ Savings opportunity found!")
            elif monthly_savings == 0:
                logger.info(f"  ℹ️  Already using optimal box")
            else:
                logger.info(f"  ℹ️  Current box is better than alternatives")
        
        # STEP 4: Update optimization run with totals
        optimization_run.products_analyzed = len(products)
        optimization_run.total_monthly_savings = total_monthly_savings
        optimization_run.total_annual_savings = total_monthly_savings * 12
        
        # Commit transaction
        self.db.commit()
        self.db.refresh(optimization_run)
        
        logger.info(f"\n=== Optimization Complete ===")
        logger.info(f"Products Analyzed: {len(products)}")
        logger.info(f"Products with Fit Boxes: {products_with_fit_boxes}")
        logger.info(f"Products with Savings: {products_with_savings}")
        logger.info(f"Products without Current Box: {products_without_current_box}")
        logger.info(f"Total Results: {len(results)}")
        logger.info(f"Total Monthly Savings: ${total_monthly_savings:.2f}")
        logger.info(f"Total Annual Savings: ${total_monthly_savings * 12:.2f}")
        
        # STEP 5: Return summary with debug info
        return OptimizationSummary(
            total_products_analyzed=len(products),
            products_with_savings=products_with_savings,
            total_monthly_savings=total_monthly_savings,
            total_annual_savings=total_monthly_savings * 12,
            results=results,
            run_id=optimization_run.id,
            timestamp=optimization_run.timestamp
        )

    # Phase 4: Multi-Product Order Packing Methods
    
    def pack_multi_product_order(
        self,
        order_items: List[Dict[str, Any]],
        available_boxes: List[Box],
        courier_rate: float = None
    ) -> Dict[str, Any]:
        """
        Pack multiple products into boxes using First Fit Decreasing algorithm.
        
        Args:
            order_items: List of {product: Product, quantity: int}
            available_boxes: List of available boxes
            courier_rate: Shipping cost per kg
            
        Returns:
            Dictionary with boxes_used, total_boxes, total_cost, success, unpacked_items
        """
        if courier_rate is None:
            courier_rate = self.DEFAULT_COURIER_RATE
        
        logger.info(f"=== Starting Multi-Product Order Packing ===")
        logger.info(f"Total order items: {len(order_items)}")
        
        # Step 1: Expand order items to individual products
        individual_products = []
        for item in order_items:
            product = item['product']
            quantity = item['quantity']
            for _ in range(quantity):
                individual_products.append(product)
        
        logger.info(f"Total individual products: {len(individual_products)}")
        
        # Step 2: Sort products by volume (descending) - First Fit Decreasing
        individual_products.sort(
            key=lambda p: p.length_cm * p.width_cm * p.height_cm,
            reverse=True
        )
        
        # Step 3: Initialize packing state
        boxes_used = []  # List of {box, products_packed, current_weight, remaining_space}
        unpacked_items = []
        
        # Step 4: Pack each product using First Fit Decreasing
        for product in individual_products:
            packed = False
            padding = self.get_category_padding(product.category)
            
            # Try to fit in existing boxes first
            for box_state in boxes_used:
                if self.can_fit_in_box(product, box_state, padding):
                    # Add product to this box
                    box_state['products_packed'].append(product)
                    box_state['current_weight'] += product.weight_kg
                    product_volume = product.length_cm * product.width_cm * product.height_cm
                    box_state['remaining_space'] -= product_volume
                    # Update fragile and stackable flags
                    product_fragile = getattr(product, 'fragile', False)
                    product_stackable = getattr(product, 'stackable', True)
                    if product_fragile:
                        box_state['has_fragile'] = True
                    if not product_stackable:
                        box_state['has_non_stackable'] = True
                    packed = True
                    logger.debug(f"  Packed '{product.name}' into existing box #{len(boxes_used)}")
                    break
            
            # If not packed, try a new box
            if not packed:
                optimal_result = self.find_optimal_box(product, available_boxes, padding)
                optimal_box = optimal_result['box']
                
                if optimal_box:
                    # Create new box state
                    box_volume = optimal_box.length_cm * optimal_box.width_cm * optimal_box.height_cm
                    product_volume = product.length_cm * product.width_cm * product.height_cm
                    
                    # Get product attributes with defaults
                    product_fragile = getattr(product, 'fragile', False)
                    product_stackable = getattr(product, 'stackable', True)
                    
                    new_box_state = {
                        'box': optimal_box,
                        'products_packed': [product],
                        'current_weight': product.weight_kg,
                        'remaining_space': box_volume - product_volume,
                        'has_fragile': product_fragile,
                        'has_non_stackable': not product_stackable
                    }
                    boxes_used.append(new_box_state)
                    packed = True
                    logger.debug(f"  Packed '{product.name}' into new box #{len(boxes_used)} (fragile={product_fragile}, stackable={product_stackable})")
                else:
                    # Cannot pack this product
                    unpacked_items.append(product)
                    logger.warning(f"  ❌ Cannot pack '{product.name}' - no suitable box")
        
        # Step 5: Calculate costs
        total_cost = 0.0
        total_shipping_cost = 0.0
        
        for box_state in boxes_used:
            box = box_state['box']
            box_cost = box.cost_per_unit
            
            # Calculate shipping cost for this box
            vol_weight = self.calculate_volumetric_weight(
                box.length_cm, box.width_cm, box.height_cm
            )
            billable_weight = self.calculate_billable_weight(
                box_state['current_weight'], vol_weight
            )
            shipping_cost = billable_weight * courier_rate
            
            total_cost += box_cost + shipping_cost
            total_shipping_cost += shipping_cost
        
        success = len(unpacked_items) == 0
        
        logger.info(f"=== Packing Complete ===")
        logger.info(f"Boxes used: {len(boxes_used)}")
        logger.info(f"Total cost: ${total_cost:.2f}")
        logger.info(f"Unpacked items: {len(unpacked_items)}")
        logger.info(f"Success: {success}")
        
        return {
            'boxes_used': boxes_used,
            'total_boxes': len(boxes_used),
            'total_cost': total_cost,
            'total_shipping_cost': total_shipping_cost,
            'success': success,
            'unpacked_items': unpacked_items
        }
    
    def can_fit_in_box(
        self,
        product: Product,
        box_state: Dict[str, Any],
        padding: float
    ) -> bool:
        """
        Check if a product can fit in the current box state.
        
        Checks:
        - Weight constraint
        - Fragile constraint
        - Stackability constraint
        - Volume constraint
        
        Args:
            product: Product to check
            box_state: Current box state with products_packed, current_weight, remaining_space
            padding: Required padding in cm
            
        Returns:
            True if product can fit
        """
        box = box_state['box']
        
        # Get product attributes with defaults if not set
        product_fragile = getattr(product, 'fragile', False)
        product_stackable = getattr(product, 'stackable', True)
        
        logger.debug(f"  Checking if '{product.name}' can fit: fragile={product_fragile}, stackable={product_stackable}")
        logger.debug(f"    Box state: has_fragile={box_state.get('has_fragile', False)}, has_non_stackable={box_state.get('has_non_stackable', False)}, items={len(box_state['products_packed'])}")
        
        # Check weight constraint
        new_weight = box_state['current_weight'] + product.weight_kg
        if new_weight > box.max_weight_kg:
            logger.debug(f"    ❌ Weight constraint failed: {new_weight} > {box.max_weight_kg}")
            return False
        
        # Check fragile constraint
        if product_fragile and len(box_state['products_packed']) > 0:
            # Fragile items cannot be stacked with other items
            logger.debug(f"    ❌ Fragile constraint failed: fragile item cannot be added to box with {len(box_state['products_packed'])} items")
            return False
        
        if box_state.get('has_fragile', False):
            # Cannot add items to a box that already has fragile items
            logger.debug(f"    ❌ Fragile constraint failed: box already has fragile items")
            return False
        
        # Check stackability constraint
        if not product_stackable and len(box_state['products_packed']) > 0:
            # Non-stackable items cannot be stacked with other items
            logger.debug(f"    ❌ Stackability constraint failed: non-stackable item cannot be added to box with {len(box_state['products_packed'])} items")
            return False
        
        if box_state.get('has_non_stackable', False):
            # Cannot add items to a box that already has non-stackable items
            logger.debug(f"    ❌ Stackability constraint failed: box already has non-stackable items")
            return False
        
        # Check volume constraint (simplified - just check remaining space)
        product_volume = product.length_cm * product.width_cm * product.height_cm
        if product_volume > box_state['remaining_space']:
            logger.debug(f"    ❌ Volume constraint failed: {product_volume} > {box_state['remaining_space']}")
            return False
        
        logger.debug(f"    ✅ Product can fit!")
        return True
