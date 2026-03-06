from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and company.
    
    Returns JWT access token upon successful registration.
    """
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    
    Rate limiting should be applied to this endpoint in production.
    """
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data)
