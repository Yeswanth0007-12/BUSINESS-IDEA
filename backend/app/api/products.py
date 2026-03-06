from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from app.core.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product for the authenticated user's company."""
    product_service = ProductService(db)
    product = product_service.create_product(product_data, current_user.company_id)
    return ProductResponse.model_validate(product)


@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products for the authenticated user's company with pagination."""
    product_service = ProductService(db)
    products = product_service.get_products(current_user.company_id, skip, limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    product_service = ProductService(db)
    product = product_service.get_product(product_id, current_user.company_id)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product."""
    product_service = ProductService(db)
    product = product_service.update_product(product_id, product_data, current_user.company_id)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product."""
    product_service = ProductService(db)
    product_service.delete_product(product_id, current_user.company_id)
    return None


@router.post("/bulk-upload", status_code=status.HTTP_201_CREATED)
async def bulk_upload_products(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk upload products from CSV file.
    
    CSV Format:
    name,sku,category,length_cm,width_cm,height_cm,weight_kg,monthly_order_volume
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        product_service = ProductService(db)
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Validate required fields
                required_fields = ['name', 'sku', 'category', 'length_cm', 'width_cm', 
                                 'height_cm', 'weight_kg', 'monthly_order_volume']
                missing_fields = [field for field in required_fields if not row.get(field)]
                
                if missing_fields:
                    errors.append(f"Row {row_num}: Missing fields: {', '.join(missing_fields)}")
                    continue
                
                # Create product data
                product_data = ProductCreate(
                    name=row['name'].strip(),
                    sku=row['sku'].strip(),
                    category=row['category'].strip(),
                    length_cm=float(row['length_cm']),
                    width_cm=float(row['width_cm']),
                    height_cm=float(row['height_cm']),
                    weight_kg=float(row['weight_kg']),
                    monthly_order_volume=int(row['monthly_order_volume'])
                )
                
                # Create product
                product_service.create_product(product_data, current_user.company_id)
                created_count += 1
                
            except ValueError as e:
                errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "success": True,
            "created_count": created_count,
            "errors": errors if errors else None,
            "message": f"Successfully created {created_count} products" + 
                      (f" with {len(errors)} errors" if errors else "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process CSV file: {str(e)}"
        )
