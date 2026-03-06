from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.user import User
from app.models.user_role import UserRoleModel
from app.core.enums import UserRole
from app.core.permissions import Permission, ROLE_PERMISSIONS
from app.schemas.role import UserRoleResponse, UserRoleAssignRequest, UserWithRoleResponse


class RBACService:
    """Role-Based Access Control service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_role(self, user_id: int) -> Optional[UserRole]:
        """Get the role for a user."""
        role_assignment = self.db.query(UserRoleModel).filter(
            UserRoleModel.user_id == user_id
        ).first()
        
        if role_assignment:
            return role_assignment.role
        return UserRole.VIEWER  # Default role
    
    def check_permission(self, user_id: int, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        role = self.get_user_role(user_id)
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    def require_permission(self, user_id: int, permission: Permission):
        """Raise exception if user doesn't have permission."""
        if not self.check_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
    
    def assign_role(self, user_email: str, role: UserRole, assigned_by_id: int, company_id: int) -> UserRoleResponse:
        """Assign a role to a user."""
        # Check if assigner has admin permission
        self.require_permission(assigned_by_id, Permission.MANAGE_USERS)
        
        # Find user by email in the same company
        user = self.db.query(User).filter(
            User.email == user_email,
            User.company_id == company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your company"
            )
        
        # Check if role assignment already exists
        existing_role = self.db.query(UserRoleModel).filter(
            UserRoleModel.user_id == user.id
        ).first()
        
        if existing_role:
            # Update existing role
            existing_role.role = role
            existing_role.granted_by = assigned_by_id
            self.db.commit()
            self.db.refresh(existing_role)
            return UserRoleResponse.model_validate(existing_role)
        else:
            # Create new role assignment
            new_role = UserRoleModel(
                user_id=user.id,
                role=role,
                granted_by=assigned_by_id
            )
            self.db.add(new_role)
            self.db.commit()
            self.db.refresh(new_role)
            return UserRoleResponse.model_validate(new_role)
    
    def list_users_with_roles(self, company_id: int) -> List[UserWithRoleResponse]:
        """List all users in a company with their roles."""
        users = self.db.query(User).filter(User.company_id == company_id).all()
        
        result = []
        for user in users:
            role = self.get_user_role(user.id)
            result.append(UserWithRoleResponse(
                id=user.id,
                email=user.email,
                company_id=user.company_id,
                role=role,
                created_at=user.created_at
            ))
        
        return result
