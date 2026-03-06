from fastapi import Request
from sqlalchemy.orm import Session
from typing import Callable

from app.core.database import get_db
from app.core.enums import AuditAction
from app.services.audit_service import AuditService
from app.models.user import User


async def audit_logging_middleware(request: Request, call_next):
    """
    Middleware to log audit events for sensitive operations.
    
    This middleware automatically logs create, update, and delete operations.
    """
    # Store request body for logging (if needed)
    body = None
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        try:
            body = await request.body()
            # Reset body for downstream handlers
            async def receive():
                return {'type': 'http.request', 'body': body}
            request._receive = receive
        except:
            pass
    
    response = await call_next(request)
    
    # Only log successful write operations (2xx status codes)
    if 200 <= response.status_code < 300 and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        user = getattr(request.state, 'user', None)
        
        if user and isinstance(user, User):
            method = request.method
            path = request.url.path
            
            action = None
            resource_type = None
            
            # Determine action and resource type
            if method == 'POST':
                action = AuditAction.CREATE
            elif method in ['PUT', 'PATCH']:
                action = AuditAction.UPDATE
            elif method == 'DELETE':
                action = AuditAction.DELETE
            
            if '/products' in path:
                resource_type = 'product'
            elif '/boxes' in path:
                resource_type = 'box'
            elif '/optimize' in path:
                resource_type = 'optimization'
            elif '/users' in path:
                resource_type = 'user'
            elif '/subscriptions' in path:
                resource_type = 'subscription'
            
            # Log audit event
            if action and resource_type:
                try:
                    db = next(get_db())
                    audit_service = AuditService(db)
                    
                    # Get client IP and user agent
                    ip_address = request.client.host if request.client else None
                    user_agent = request.headers.get('user-agent')
                    
                    audit_service.log_action(
                        company_id=user.company_id,
                        user_id=user.id,
                        action=action,
                        resource_type=resource_type,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Audit logging error: {e}")
                finally:
                    db.close()
    
    return response
