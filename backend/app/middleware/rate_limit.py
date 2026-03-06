from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, use Redis-based rate limiting like slowapi or fastapi-limiter.
    This implementation is for demonstration purposes.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Use X-Forwarded-For if behind proxy, otherwise use client host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_id: str):
        """Remove requests older than 1 minute"""
        cutoff = datetime.now() - timedelta(minutes=1)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        # Clean old requests
        self._clean_old_requests(client_id)
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        self.requests[client_id].append(datetime.now())
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        return response
