from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services.rbac_service import RBACService
from app.models.user import User
from app.schemas.role import UserRoleAssignRequest, UserWithRoleResponse
from app.middleware.rbac_middleware import require_admin


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserWithRoleResponse])
def list_company_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users in the company with their roles.
    
    Requires: Admin role
    """
    rbac_service = RBACService(db)
    return rbac_service.list_users_with_roles(current_user.company_id)


@router.post("/users/assign-role")
def assign_user_role(
    request: UserRoleAssignRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Assign a role to a user.
    
    Requires: Admin role
    """
    rbac_service = RBACService(db)
    return rbac_service.assign_role(
        user_email=request.user_email,
        role=request.role,
        assigned_by_id=current_user.id,
        company_id=current_user.company_id
    )
