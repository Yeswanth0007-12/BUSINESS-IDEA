"""
Redis-based rate limiting for warehouse API with tier-based limits.
"""
from fastapi import Request, HTTPException, status
from typing import Optional
import redis
from datetime import datetime
import os


class WarehouseRateLimiter:
    """
    Redis-based rate limiter for warehouse API endpoints.
    
    Supports tier-based rate limits:
    - Standard tier: 100 requests/minute
    - Premium tier: 500 requests/minute
    - Enterprise tier: 2000 requests/minute
    """
    
    # Rate limits per tier (requests per minute)
    TIER_LIMITS = {
        "standard": 100,
        "premium": 500,
        "enterprise": 2000
    }
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize rate limiter with Redis client.
        
        Args:
            redis_client: Redis client instance (optional, will create if not provided)
        """
        if redis_client is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis = redis_client
    
    def get_rate_limit(self, tier: str) -> int:
        """
        Get rate limit for a subscription tier.
        
        Args:
            tier: Subscription tier (standard, premium, enterprise)
            
        Returns:
            Rate limit in requests per minute
        """
        return self.TIER_LIMITS.get(tier.lower(), self.TIER_LIMITS["standard"])
    
    def check_rate_limit(self, api_key_id: int, tier: str = "standard") -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        
        Args:
            api_key_id: API key ID for tracking
            tier: Subscription tier
            
        Returns:
            Tuple of (is_allowed, remaining_requests, retry_after_seconds)
        """
        # Get rate limit for tier
        limit = self.get_rate_limit(tier)
        
        # Redis key for this API key
        key = f"rate_limit:warehouse:{api_key_id}"
        
        # Get current count
        try:
            current = self.redis.get(key)
            if current is None:
                # First request in this window
                self.redis.setex(key, 60, 1)  # Set with 60 second expiry
                return True, limit - 1, 0
            
            current = int(current)
            
            if current >= limit:
                # Rate limit exceeded
                ttl = self.redis.ttl(key)
                return False, 0, max(ttl, 1)
            
            # Increment counter
            self.redis.incr(key)
            return True, limit - current - 1, 0
            
        except redis.RedisError as e:
            # If Redis fails, allow the request (fail open)
            print(f"Redis error in rate limiter: {e}")
            return True, limit, 0
    
    def reset_rate_limit(self, api_key_id: int):
        """
        Reset rate limit for an API key (for testing or admin purposes).
        
        Args:
            api_key_id: API key ID
        """
        key = f"rate_limit:warehouse:{api_key_id}"
        self.redis.delete(key)


async def check_warehouse_rate_limit(
    request: Request,
    api_key_id: int,
    tier: str = "standard"
):
    """
    FastAPI dependency to check warehouse API rate limit.
    
    Args:
        request: FastAPI request object
        api_key_id: API key ID from authentication
        tier: Subscription tier
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Get or create rate limiter
    if not hasattr(request.app.state, "warehouse_rate_limiter"):
        request.app.state.warehouse_rate_limiter = WarehouseRateLimiter()
    
    rate_limiter = request.app.state.warehouse_rate_limiter
    
    # Check rate limit
    is_allowed, remaining, retry_after = rate_limiter.check_rate_limit(api_key_id, tier)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
    
    # Add rate limit headers to response (will be added by middleware)
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = rate_limiter.get_rate_limit(tier)
