from arq import create_pool
from arq.connections import RedisSettings
from .config import settings
from .core.logging import get_logger

logger = get_logger(__name__)

redis_pool = None

async def get_redis_pool():
    """Get or create the Redis connection pool for ARQ"""
    global redis_pool
    if redis_pool is None:
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return redis_pool

async def close_redis_pool():
    """Graceful shutdown of the Redis pool"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None
