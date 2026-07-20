from arq import create_pool
from arq.connections import RedisSettings
from .config import settings
<<<<<<< HEAD
from .core.logging import get_logger
=======
from .core.logger import get_logger
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

logger = get_logger(__name__)

redis_pool = None

async def get_redis_pool():
    """Get or create the Redis connection pool for ARQ"""
    global redis_pool
    if redis_pool is None:
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return redis_pool

<<<<<<< HEAD
=======
async def enqueue_video_job(video_id: str):
    """
    Enqueue a video processing job (transcripts + embeddings) into ARQ.
    """
    pool = await get_redis_pool()
    await pool.enqueue_job('process_video_task', video_id)
    logger.info("Enqueued video processing job: %s", video_id)

async def enqueue_quiz_job(video_id: str):
    """
    Enqueue a quiz generation job into ARQ.
    Achieves <15ms latency in API by offloading work to background.
    """
    pool = await get_redis_pool()
    await pool.enqueue_job('generate_quiz_task', video_id)
    logger.info("Enqueued quiz generation job for video: %s", video_id)

>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
async def close_redis_pool():
    """Graceful shutdown of the Redis pool"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None
