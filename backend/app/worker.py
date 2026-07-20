import asyncio
from arq.connections import RedisSettings
from .database import db, init_firebase, ensure_indexes
from .services.gemini_service import gemini_service
from .services.processing_queue_service import processing_worker
from .config import settings
<<<<<<< HEAD
from .core.logging import get_logger
=======
from .core.logger import get_logger
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
from datetime import datetime, timezone

logger = get_logger(__name__)

async def process_video_task(ctx, video_id: str):
    """
    ARQ Background Task to fetch transcript and generate embeddings.
    Routes through the semaphore on processing_worker so only one
    transcript is fetched at a time, avoiding YouTube rate-limits.
    Then enqueues the quiz generation task.
    """
<<<<<<< HEAD
    logger.info(f"📹 Processing video for embeddings: {video_id}")
=======
    logger.info("Processing video for embeddings: %s", video_id)
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
    try:
        # Check if there is an existing job in processing_queue to keep status in sync
        job = await db.processing_queue.find_one({"video_id": video_id})
        if not job:
            # Create a dummy job dict if not found
            job = {"video_id": video_id, "_id": None}
        
        # Use semaphore-gated method to ensure only 1 transcript is fetched at a time
        await processing_worker._process_with_semaphore(job)
<<<<<<< HEAD
        logger.info(f"✅ Video processing (embeddings) finished for {video_id}")
    except Exception as e:
        logger.error(f"❌ Error in process_video_task for {video_id}: {e}", exc_info=True)
        raise e

async def generate_quiz_logic(video_id: str):
    """
    Core logic to generate a quiz for a video.
    Extracted from generate_quiz_task to allow direct calls without ARQ.
    """
    logger.info(f"📦 Processing quiz for video: {video_id}")
=======
        logger.info("Video processing (embeddings) finished for %s", video_id)
    except Exception as e:
        logger.error("Error in process_video_task for %s: %s", video_id, e)
        raise e

async def generate_quiz_task(ctx, video_id: str):
    """
    ARQ Background Task to generate a quiz for a video.
    """
    logger.info("Processing quiz for video: %s", video_id)
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
    
    try:
        # 1. Fetch video from database
        video = await db.videos.find_one({"id": video_id})
        if not video:
<<<<<<< HEAD
            logger.error(f"❌ Video {video_id} not found in database")
            return False
            
        transcript = video.get("transcript", "")
        if not transcript:
            logger.warning(f"⚠️ Video {video_id} has no transcript. Cannot generate quiz.")
            return False

        # 2. Generate quiz via Gemini AI
        logger.info(f"  🧠 Calling Gemini AI for quiz generation...")
=======
            logger.error("Video %s not found in database", video_id)
            return
            
        transcript = video.get("transcript", "")
        if not transcript:
            logger.warning("Video %s has no transcript. Cannot generate quiz.", video_id)
            return

        # 2. Generate quiz via Gemini AI
        logger.info("Calling Gemini AI for quiz generation...")
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
        questions = await gemini_service.generate_quiz(
            video_title=video["title"],
            video_transcript=transcript,
            topics=video.get("topics", []),
            difficulty=video.get("difficulty", "Medium"),
            num_questions=4
        )

        if not questions or len(questions) < 4:
            raise Exception(f"AI failed to generate enough valid questions for {video_id}")

        # 3. Save to quizzes collection
        quiz_doc = {
            "id": f"quiz-{video_id}",
            "video_id": video_id,
            "questions": questions,
            "generated_at": datetime.now(timezone.utc)
        }
        
        await db.quizzes.update_one(
            {"video_id": video_id},
            {"$set": quiz_doc},
            upsert=True
        )
        
<<<<<<< HEAD
        logger.info(f"✅ Quiz generated and saved for {video_id} ({len(questions)} questions)")
        return True

    except Exception as e:
        logger.error(f"❌ Error generating quiz for {video_id}: {e}", exc_info=True)
        raise e

async def generate_quiz_task(ctx, video_id: str):
    """
    ARQ Background Task wrapper for quiz generation.
    """
    await generate_quiz_logic(video_id)

=======
        logger.info("Quiz generated and saved for %s (%d questions)", video_id, len(questions))

    except Exception as e:
        logger.error("Error generating quiz for %s: %s", video_id, e)
        raise e

>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
async def startup(ctx):
    """Worker startup logic"""
    init_firebase()
    await ensure_indexes()
<<<<<<< HEAD
    logger.info("🚀 ARQ Worker started. Ready for jobs (Embeddings + Quizzes).")

async def shutdown(ctx):
    """Worker shutdown logic"""
    logger.info("⏹️ ARQ Worker shutting down.")
=======
    logger.info("ARQ Worker started. Ready for jobs (Embeddings + Quizzes).")

async def shutdown(ctx):
    """Worker shutdown logic"""
    logger.info("ARQ Worker shutting down.")
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

class WorkerSettings:
    """ARQ Worker configuration"""
    functions = [process_video_task, generate_quiz_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    concurrency = 3
    max_retries = 3
    retry_delay_seconds = 10
