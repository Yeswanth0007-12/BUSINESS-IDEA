from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import csv
import io

from app.core.database import get_db
from app.models.user import User
from app.schemas.box import BoxCreate, BoxUpdate, BoxResponse
from app.services.box_service import BoxService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/boxes", tags=["Boxes"])


@router.post("", response_model=BoxResponse, status_code=status.HTTP_201_CREATED)
def create_box(
    box_data: BoxCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new box for the authenticated user's company."""
    box_service = BoxService(db)
    box = box_service.create_box(box_data, current_user.company_id)
    return BoxResponse.model_validate(box)


@router.get("", response_model=List[BoxResponse])
def get_boxes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all boxes for the authenticated user's company."""
    box_service = BoxService(db)
    boxes = box_service.get_boxes(current_user.company_id)
    return [BoxResponse.model_validate(b) for b in boxes]


@router.get("/{box_id}", response_model=BoxResponse)
def get_box(
    box_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific box by ID."""
    box_service = BoxService(db)
    box = box_service.get_box(box_id, current_user.company_id)
    return BoxResponse.model_validate(box)


@router.put("/{box_id}", response_model=BoxResponse)
def update_box(
    box_id: int,
    box_data: BoxUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a box."""
    box_service = BoxService(db)
    box = box_service.update_box(box_id, box_data, current_user.company_id)
    return BoxResponse.model_validate(box)


@router.delete("/{box_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_box(
    box_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a box."""
    box_service = BoxService(db)
    box_service.delete_box(box_id, current_user.company_id)
    return None


@router.post("/bulk-upload", status_code=status.HTTP_201_CREATED)
async def bulk_upload_boxes(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk upload boxes from CSV file.
    
    CSV Format:
    name,length_cm,width_cm,height_cm,cost_per_unit
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
        
        box_service = BoxService(db)
        created_count = 0
        errors = []
        
        # Get fieldnames to debug
        fieldnames = csv_reader.fieldnames
        print(f"CSV Headers detected: {fieldnames}")
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Debug: Print first row
                if row_num == 2:
                    print(f"First row data: {row}")
                
                # Validate required fields
                required_fields = ['name', 'length_cm', 'width_cm', 'height_cm', 'cost_per_unit']
                missing_fields = [field for field in required_fields if not row.get(field) or not row.get(field).strip()]
                
                if missing_fields:
                    errors.append(f"Row {row_num}: Missing or empty fields: {', '.join(missing_fields)}")
                    continue
                
                # Create box data
                box_data = BoxCreate(
                    name=row['name'].strip(),
                    length_cm=float(row['length_cm'].strip()),
                    width_cm=float(row['width_cm'].strip()),
                    height_cm=float(row['height_cm'].strip()),
                    cost_per_unit=float(row['cost_per_unit'].strip())
                )
                
                # Create box
                box_service.create_box(box_data, current_user.company_id)
                created_count += 1
                
            except ValueError as e:
                errors.append(f"Row {row_num}: Invalid data format - {str(e)}")
            except KeyError as e:
                errors.append(f"Row {row_num}: Missing column {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        print(f"Upload complete: {created_count} created, {len(errors)} errors")
        
        return {
            "success": True,
            "created_count": created_count,
            "errors": errors if errors else None,
            "message": f"Successfully created {created_count} boxes" + 
                      (f" with {len(errors)} errors" if errors else "")
        }
        
    except Exception as e:
        print(f"CSV Upload Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process CSV file: {str(e)}"
        )
