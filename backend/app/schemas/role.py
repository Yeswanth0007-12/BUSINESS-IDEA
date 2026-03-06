from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.core.enums import UserRole


class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role: UserRole
    granted_at: datetime
    granted_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserRoleAssignRequest(BaseModel):
    user_email: EmailStr
    role: UserRole


class UserWithRoleResponse(BaseModel):
    id: int
    email: str
    company_id: int
    role: Optional[UserRole] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
