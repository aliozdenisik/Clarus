"""
Redis async connection manager for Clarus backend.

Provides:
- RedisManager: Async connection pool management
- get_redis(): FastAPI dependency for accessing Redis client
- redis_manager: Global instance for lifespan management
"""

from redis import asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class RedisManager:
    """
    Async Redis connection manager with connection pooling.

    Handles:
    - Connection pool creation with optimized settings
    - Graceful startup (fail-open if Redis unavailable)
    - Health checks
    - Cleanup on shutdown
    """

    def __init__(self):
        """Initialize Redis manager with no client."""
        self.client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """
        Connect to Redis with connection pool.

        Configuration:
        - max_connections=50: Connection pool size
        - socket_keepalive=True: TCP keepalive for long-lived connections
        - health_check_interval=30: Periodic health checks (seconds)
        - decode_responses=False: Keep binary for embedding data
        - socket_timeout=5: Socket timeout (seconds)
        - retry_on_timeout=True: Retry on timeout

        On failure: Logs warning and sets client=None (fail-open).
        Does NOT raise exception to prevent startup blocking.
        """
        try:
            # Create connection pool with optimized settings
            pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=50,
                socket_keepalive=True,
                health_check_interval=30,
                decode_responses=False,
                socket_timeout=5,
                retry_on_timeout=True,
            )

            # Create Redis client from pool
            self.client = aioredis.Redis(connection_pool=pool)

            # Test connection with ping
            await self.client.ping()
            logger.info("Redis connection established and verified")

        except Exception as e:
            # Fail-open: Log warning but don't raise
            logger.warning(
                "Failed to connect to Redis",
                extra={
                    "error_type": type(e).__name__,
                    "redis_host": settings.redis_host,
                    "redis_port": settings.redis_port,
                },
            )
            self.client = None

    async def disconnect(self) -> None:
        """
        Close Redis connection and cleanup pool.

        Safe to call even if client is None.
        """
        if self.client:
            try:
                await self.client.aclose()
                self.client = None
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(
                    "Error closing Redis connection",
                    extra={"error_type": type(e).__name__},
                )

    async def health_check(self) -> bool:
        """
        Check Redis health with ping.

        Returns:
            True if Redis is healthy, False otherwise.
        """
        if not self.client:
            return False

        try:
            await self.client.ping()
            return True
        except Exception:
            return False


# Global instance for lifespan management
redis_manager = RedisManager()


async def get_redis() -> aioredis.Redis | None:
    """
    FastAPI dependency for accessing Redis client.

    Returns:
        Redis client or None if unavailable.

    Usage in route:
        @router.get("/example")
        async def example(redis: aioredis.Redis | None = Depends(get_redis)):
            if redis:
                await redis.set("key", "value")
    """
    return redis_manager.client
