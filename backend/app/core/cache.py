"""
Redis caching utilities for performance optimization.
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis
from redis.asyncio import Redis as AsyncRedis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages Redis caching operations with both sync and async support."""
    
    def __init__(self):
        self.redis_client = None
        self.async_redis_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Redis clients."""
        try:
            # Sync Redis client
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Async Redis client
            self.async_redis_client = AsyncRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.async_redis_client = None
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a standardized cache key."""
        return f"{settings.REDIS_KEY_PREFIX}:{prefix}:{identifier}"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0
    
    async def async_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Async version of set."""
        if not self.async_redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            if ttl:
                return await self.async_redis_client.setex(key, ttl, serialized_value)
            else:
                return await self.async_redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Async cache set error for key {key}: {e}")
            return False
    
    async def async_get(self, key: str) -> Optional[Any]:
        """Async version of get."""
        if not self.async_redis_client:
            return None
        
        try:
            value = await self.async_redis_client.get(key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Async cache get error for key {key}: {e}")
            return None


# Cache TTL constants (in seconds)
class CacheTTL:
    CURRICULUM_CONTENT = 3600 * 24  # 24 hours
    USER_PROGRESS = 300  # 5 minutes
    ASSESSMENT_QUESTIONS = 1800  # 30 minutes
    AI_RESPONSES = 3600  # 1 hour
    LESSON_CONTENT = 3600 * 12  # 12 hours
    ANALYTICS_DATA = 600  # 10 minutes


# Cache key prefixes
class CacheKeys:
    CURRICULUM = "curriculum"
    LESSON = "lesson"
    ASSESSMENT = "assessment"
    PROGRESS = "progress"
    AI_CONTEXT = "ai_context"
    ANALYTICS = "analytics"
    USER_SESSION = "user_session"


# Global cache manager instance
cache_manager = CacheManager()


def cache_curriculum_content(level_id: str, section_id: str = None, topic_id: str = None):
    """Decorator for caching curriculum content."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key based on parameters
            if topic_id:
                cache_key = cache_manager._generate_key(CacheKeys.CURRICULUM, f"topic:{topic_id}")
            elif section_id:
                cache_key = cache_manager._generate_key(CacheKeys.CURRICULUM, f"section:{section_id}")
            else:
                cache_key = cache_manager._generate_key(CacheKeys.CURRICULUM, f"level:{level_id}")
            
            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, CacheTTL.CURRICULUM_CONTENT)
                logger.info(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator


def cache_ai_response(context_hash: str, ttl: int = CacheTTL.AI_RESPONSES):
    """Decorator for caching AI agent responses."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = cache_manager._generate_key(CacheKeys.AI_CONTEXT, context_hash)
            
            # Try cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"AI cache hit for {cache_key}")
                return cached_result
            
            # Execute and cache
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
                logger.info(f"Cached AI response for {cache_key}")
            
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a specific user."""
    patterns = [
        cache_manager._generate_key(CacheKeys.PROGRESS, f"user:{user_id}:*"),
        cache_manager._generate_key(CacheKeys.USER_SESSION, f"{user_id}:*"),
        cache_manager._generate_key(CacheKeys.ANALYTICS, f"user:{user_id}:*")
    ]
    
    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += cache_manager.invalidate_pattern(pattern)
    
    logger.info(f"Invalidated {total_invalidated} cache entries for user {user_id}")
    return total_invalidated