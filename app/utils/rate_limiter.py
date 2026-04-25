from fastapi import HTTPException, status, Depends
from utils.auth import get_current_user
from utils.cache import generate_cache_key, get_cached_data, set_cached_data
from models.user import User
import redis
import os

# Redis client for rate limiting
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

def rate_limit(endpoint: str, max_requests: int, window_seconds: int):
    """
    Rate limit decorator factory
    
    Args:
        endpoint: Name of endpoint (e.g., "import_playlist")
        max_requests: Max requests allowed
        window_seconds: Time window in seconds
    """
    async def rate_limit_dependency(current_user: User = Depends(get_current_user)):
        # Create unique key for this user + endpoint
        key = f"rate_limit:user:{current_user.id}:{endpoint}"
        
        try:
            # Get current count from Redis
            current_count = redis_client.get(key)
            
            if current_count is None:
                # First request - set counter to 1 with expiry
                redis_client.setex(key, window_seconds, 1)
            else:
                current_count = int(current_count)
                
                if current_count >= max_requests:
                    # Rate limit exceeded
                    ttl = redis_client.ttl(key)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {ttl} seconds."
                    )
                
                # Increment counter
                redis_client.incr(key)
        
        except redis.RedisError:
            # If Redis fails, allow request (fail-open)
            print(f"[WARN] Redis error in rate limiter for '{endpoint}' — allowing request (fail-open)")
            pass
        
        return current_user
    
    return rate_limit_dependency