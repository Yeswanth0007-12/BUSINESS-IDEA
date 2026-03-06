from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse


class ProductService:
    """Service for managing products with multi-tenant isolation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate, company_id: int) -> Product:
        """
        Create a new product with SKU uniqueness check.
        
        Args:
            product_data: Product creation data
            company_id: Company ID for multi-tenant isolation
            
        Returns:
            Created product
            
        Raises:
            HTTPException: If SKU already exists for this company
        """
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating product: name={product_data.name}, fragile={product_data.fragile}, stackable={product_data.stackable}")
        
        # Check if SKU already exists for this company
        existing_product = self.db.query(Product).filter(
            Product.company_id == company_id,
            Product.sku == product_data.sku
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_data.sku}' already exists"
            )
        
        # Create new product
        new_product = Product(
            company_id=company_id,
            name=product_data.name,
            sku=product_data.sku,
            category=product_data.category,
            length_cm=product_data.length_cm,
            width_cm=product_data.width_cm,
            height_cm=product_data.height_cm,
            weight_kg=product_data.weight_kg,
            current_box_id=product_data.current_box_id,
            monthly_order_volume=product_data.monthly_order_volume,
            fragile=product_data.fragile,
            stackable=product_data.stackable
        )
        
        logger.info(f"Product object created: fragile={new_product.fragile}, stackable={new_product.stackable}")
        
        try:
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            logger.info(f"Product saved to DB: fragile={new_product.fragile}, stackable={new_product.stackable}")
            return new_product
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create product. Check that current_box_id is valid."
            )
    
    def get_products(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """
        Get all products for a company with pagination.
        
        Args:
            company_id: Company ID for multi-tenant isolation
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of products
        """
        return self.db.query(Product).filter(
            Product.company_id == company_id
        ).offset(skip).limit(limit).all()
    
    def get_product(self, product_id: int, company_id: int) -> Product:
        """
        Get a single product with ownership verification.
        
        Args:
            product_id: Product ID
            company_id: Company ID for ownership verification
            
        Returns:
            Product object
            
        Raises:
            HTTPException: If product not found or doesn't belong to company
        """
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
    
    def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate,
        company_id: int
    ) -> Product:
        """
        Update a product with ownership verification.
        
        Args:
            product_id: Product ID
            product_data: Product update data
            company_id: Company ID for ownership verification
            
        Returns:
            Updated product
            
        Raises:
            HTTPException: If product not found or doesn't belong to company
        """
        product = self.get_product(product_id, company_id)
        
        # Update fields if provided
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Check SKU uniqueness if SKU is being updated
        if "sku" in update_data and update_data["sku"] != product.sku:
            existing_product = self.db.query(Product).filter(
                Product.company_id == company_id,
                Product.sku == update_data["sku"],
                Product.id != product_id
            ).first()
            
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with SKU '{update_data['sku']}' already exists"
                )
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(product)
            return product
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update product. Check that current_box_id is valid."
            )
    
    def delete_product(self, product_id: int, company_id: int) -> None:
        """
        Delete a product with ownership verification.
        
        Args:
            product_id: Product ID
            company_id: Company ID for ownership verification
            
        Raises:
            HTTPException: If product not found or doesn't belong to company
        """
        product = self.get_product(product_id, company_id)
        
        self.db.delete(product)
        self.db.commit()
