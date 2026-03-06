from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Callable

from app.core.database import get_db
from app.core.enums import UsageAction
from app.services.usage_service import UsageService
from app.models.user import User


async def track_usage_middleware(request: Request, call_next):
    """
    Middleware to track usage events.
    
    This middleware automatically tracks API usage for authenticated requests.
    """
    response = await call_next(request)
    
    # Only track successful requests (2xx status codes)
    if 200 <= response.status_code < 300:
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, 'user', None)
        
        if user and isinstance(user, User):
            # Determine action based on HTTP method and path
            method = request.method
            path = request.url.path
            
            action = None
            resource_type = None
            
            if '/products' in path:
                resource_type = 'product'
                if method == 'POST':
                    action = UsageAction.CREATE
                elif method == 'PUT' or method == 'PATCH':
                    action = UsageAction.UPDATE
                elif method == 'DELETE':
                    action = UsageAction.DELETE
                elif method == 'GET':
                    action = UsageAction.READ
            
            elif '/boxes' in path:
                resource_type = 'box'
                if method == 'POST':
                    action = UsageAction.CREATE
                elif method == 'PUT' or method == 'PATCH':
                    action = UsageAction.UPDATE
                elif method == 'DELETE':
                    action = UsageAction.DELETE
                elif method == 'GET':
                    action = UsageAction.READ
            
            elif '/optimize' in path:
                resource_type = 'optimization'
                action = UsageAction.OPTIMIZE
            
            # Track usage if action and resource type are determined
            if action and resource_type:
                try:
                    db = next(get_db())
                    usage_service = UsageService(db)
                    usage_service.track_usage(
                        company_id=user.company_id,
                        user_id=user.id,
                        action=action,
                        resource_type=resource_type
                    )
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Usage tracking error: {e}")
                finally:
                    db.close()
    
    return response
