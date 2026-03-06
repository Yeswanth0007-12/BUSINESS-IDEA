from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import hashlib
import secrets
import hmac
from datetime import datetime

from app.models.user import User
from app.models.company import Company
from app.models.user_role import UserRoleModel
from app.models.api_key import ApiKey
from app.schemas.user import UserCreate, UserLogin, Token, TokenData, UserResponse
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, verify_token
from app.core.database import get_db
from app.core.enums import UserRole


security = HTTPBearer()


class AuthService:
    """Authentication service for user registration and login."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> Token:
        """
        Register a new user and company.
        
        Args:
            user_data: User registration data
            
        Returns:
            JWT token for the new user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if company already exists
        company = self.db.query(Company).filter(Company.name == user_data.company_name).first()
        
        # Create company if it doesn't exist
        if not company:
            company = Company(name=user_data.company_name)
            self.db.add(company)
            self.db.flush()  # Get company ID without committing
        
        # Create user
        hashed_pwd = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_pwd,
            company_id=company.id
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Assign ADMIN role to new user
        user_role = UserRoleModel(
            user_id=new_user.id,
            role=UserRole.ADMIN
        )
        self.db.add(user_role)
        self.db.commit()
        
        # Create access token
        token_data = {"sub": str(new_user.id), "company_id": new_user.company_id}
        access_token = create_access_token(data=token_data)
        
        return Token(access_token=access_token)
    
    def authenticate_user(self, login_data: UserLogin) -> Token:
        """
        Authenticate a user and return JWT token.
        
        Args:
            login_data: User login credentials
            
        Returns:
            JWT token for authenticated user
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        token_data = {"sub": str(user.id), "company_id": user.company_id}
        access_token = create_access_token(data=token_data)
        
        return Token(access_token=access_token)
    
    def verify_token(self, token: str) -> TokenData:
        """
        Verify JWT token and extract user data.
        
        Args:
            token: JWT token string
            
        Returns:
            Token data with user_id and company_id
            
        Raises:
            HTTPException: If token is invalid
        """
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id: Optional[str] = payload.get("sub")
        company_id: Optional[int] = payload.get("company_id")
        
        if user_id is None or company_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return TokenData(user_id=int(user_id), company_id=company_id)
    
    def get_current_user(self, token_data: TokenData) -> User:
        """
        Get current user from token data.
        
        Args:
            token_data: Verified token data
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == token_data.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user


def generate_api_key() -> str:
    """
    Generate a random API key.
    
    Returns:
        Base64-encoded random API key
    """
    # Generate 32 random bytes
    random_bytes = secrets.token_bytes(32)
    # Encode as base64 and add prefix
    api_key = f"pk_live_{secrets.token_urlsafe(32)}"
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256.
    
    Args:
        api_key: Plaintext API key
        
    Returns:
        SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal, False otherwise
    """
    return hmac.compare_digest(a, b)


def authenticate_api_key(db: Session, api_key: str) -> Optional[ApiKey]:
    """
    Authenticate an API key and return the associated ApiKey object.
    
    Args:
        db: Database session
        api_key: Plaintext API key from request
        
    Returns:
        ApiKey object if valid, None otherwise
    """
    # Hash the provided API key
    key_hash = hash_api_key(api_key)
    
    # Query for matching API key
    stored_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    ).first()
    
    if not stored_key:
        return None
    
    # Use constant-time comparison for additional security
    if not constant_time_compare(key_hash, stored_key.key_hash):
        return None
    
    # Update last_used_at timestamp
    stored_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return stored_key


def create_api_key(db: Session, company_id: int, name: str) -> tuple[ApiKey, str]:
    """
    Create a new API key for a company.
    
    Args:
        db: Database session
        company_id: Company ID
        name: Descriptive name for the API key
        
    Returns:
        Tuple of (ApiKey object, plaintext API key)
    """
    # Generate new API key
    plaintext_key = generate_api_key()
    key_hash = hash_api_key(plaintext_key)
    
    # Create API key record
    api_key = ApiKey(
        company_id=company_id,
        key_hash=key_hash,
        name=name
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key, plaintext_key


# Dependency functions for FastAPI endpoints
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user.
    
    Args:
        credentials: HTTP Bearer token from request
        db: Database session
        
    Returns:
        Current authenticated user
    """
    auth_service = AuthService(db)
    token_data = auth_service.verify_token(credentials.credentials)
    return auth_service.get_current_user(token_data)
