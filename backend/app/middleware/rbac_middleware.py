from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Callable

from app.core.database import get_db
from app.core.permissions import Permission
from app.services.rbac_service import RBACService
from app.services.auth_service import get_current_user
from app.models.user import User


def require_permission(permission: Permission):
    """
    Dependency factory for requiring specific permissions.
    
    Usage:
        @router.post("/products", dependencies=[Depends(require_permission(Permission.CREATE_PRODUCT))])
    """
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        rbac_service = RBACService(db)
        rbac_service.require_permission(current_user.id, permission)
        return current_user
    
    return permission_checker


def require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency for requiring admin role."""
    rbac_service = RBACService(db)
    rbac_service.require_permission(current_user.id, Permission.MANAGE_USERS)
    return current_user
