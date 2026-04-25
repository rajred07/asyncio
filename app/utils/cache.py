import redis
import json
import hashlib
from typing import Optional
import os

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
YOUTUBE_CACHE_TTL = int(os.getenv("YOUTUBE_CACHE_TTL", 604800))  # 7 days
FEED_CACHE_TTL = int(os.getenv("FEED_CACHE_TTL", 300))           # 5 minutes

# Create Redis connection pool (reusable connections)
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True  # Auto-decode bytes to strings
)

def generate_cache_key(prefix: str, identifier: str) -> str:
    """
    Generate a consistent cache key
    Example: youtube:video:dQw4w9WgXcQ
    """
    # Use hash for long URLs to keep keys short
    if len(identifier) > 50:
        identifier = hashlib.md5(identifier.encode()).hexdigest()
    return f"{prefix}:{identifier}"

def get_cached_data(key: str) -> Optional[dict]:
    """
    Retrieve data from Redis cache
    Returns None if not found or expired
    """
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        print(f"❌ Redis GET Error: {e}")
        return None

def set_cached_data(key: str, data: dict, ttl: int = None) -> bool:
    """
    Store data in Redis cache with TTL (Time To Live)
    
    Args:
        key: Cache key
        data: Dictionary to cache
        ttl: Expiration time in seconds (default: 7 days)
    """
    try:
        if ttl is None:
            ttl = YOUTUBE_CACHE_TTL
        
        redis_client.setex(
            name=key,
            time=ttl,
            value=json.dumps(data)
        )
        return True
    except Exception as e:
        print(f"❌ Redis SET Error: {e}")
        return False

def delete_cached_data(key: str) -> bool:
    """Delete data from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"❌ Redis DELETE Error: {e}")
        return False

def clear_youtube_cache(video_id: str = None):
    """
    Clear YouTube cache (useful for testing or manual refresh)
    If video_id provided, clears only that video
    Otherwise, clears all YouTube cache
    """
    try:
        if video_id:
            key = generate_cache_key("youtube:video", video_id)
            redis_client.delete(key)
        else:
            # Clear all keys matching pattern
            for key in redis_client.scan_iter("youtube:*"):
                redis_client.delete(key)
        return True
    except Exception as e:
        print(f"❌ Redis CLEAR Error: {e}")
        return False

def get_cache_stats() -> dict:
    """Get cache statistics (useful for monitoring)"""
    try:
        info = redis_client.info()
        return {
            "connected": True,
            "used_memory_human": info.get("used_memory_human", "N/A"),
            "total_keys": redis_client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / 
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 
                2
            )
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


# ---------------------------------------------------------------------------
# JWT Token Blacklist
# ---------------------------------------------------------------------------

def blacklist_token(jti: str, ttl_seconds: int) -> bool:
    """
    Add a token's jti to the blacklist when user logs out.
    ttl_seconds should equal the remaining lifetime of the JWT so Redis
    auto-expires the key when the token would have expired anyway.
    """
    try:
        redis_client.setex(f"blacklist:jwt:{jti}", ttl_seconds, "1")
        return True
    except Exception as e:
        print(f"❌ Redis BLACKLIST SET Error: {e}")
        return False


def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a token's jti has been blacklisted (i.e. the user logged out).
    Returns True if the token should be REJECTED.
    Falls back to False (allow) if Redis is unreachable — so auth still works
    even if Redis goes down.
    """
    try:
        return redis_client.exists(f"blacklist:jwt:{jti}") == 1
    except Exception as e:
        print(f"⚠️  Redis BLACKLIST CHECK Error (allowing token): {e}")
        return False  # Fail-open: don't lock out users if Redis is down


# ---------------------------------------------------------------------------
# Feed Cache
# ---------------------------------------------------------------------------

def get_feed_cache(key: str) -> Optional[dict]:
    """Get a cached feed response. Returns None on miss or Redis error."""
    try:
        cached = redis_client.get(f"feed:{key}")
        return json.loads(cached) if cached else None
    except Exception as e:
        print(f"⚠️  Redis FEED GET Error (skipping cache): {e}")
        return None


def set_feed_cache(key: str, data: dict, ttl: int = FEED_CACHE_TTL) -> None:
    """Cache a feed response for TTL seconds (default 5 minutes)."""
    try:
        redis_client.setex(f"feed:{key}", ttl, json.dumps(data, default=str))
    except Exception as e:
        print(f"⚠️  Redis FEED SET Error (continuing without cache): {e}")


def invalidate_feed_cache(user_id: int) -> None:
    """
    Invalidate all feed cache keys for a specific user.
    Called after the user likes/saves/follows — so next load is fresh.
    """
    try:
        for key in redis_client.scan_iter(f"feed:for_you:{user_id}:*"):
            redis_client.delete(key)
        for key in redis_client.scan_iter(f"feed:following:{user_id}:*"):
            redis_client.delete(key)
    except Exception as e:
        print(f"⚠️  Redis FEED INVALIDATE Error: {e}")