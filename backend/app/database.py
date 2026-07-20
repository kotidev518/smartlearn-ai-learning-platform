import os
<<<<<<< HEAD
=======
import json
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
import firebase_admin
from firebase_admin import credentials
from motor.motor_asyncio import AsyncIOMotorClient
from .core.config import settings
<<<<<<< HEAD
from .core.logging import get_logger
=======
from .core.logger import get_logger
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
from .db.session import db_manager

logger = get_logger(__name__)

# Backward compatibility for existing code
db = db_manager.get_db()

def init_firebase():
<<<<<<< HEAD
    """Initialize Firebase Admin with proper error handling and configuration."""
    try:
        if not firebase_admin._apps:
            cred_path = settings.get_firebase_credentials_path()
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                })
                logger.info("Firebase Admin initialized successfully")
            else:
                logger.warning(f"Firebase credentials not found at {cred_path}")
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin: {e}", exc_info=True)
=======
    """Initialize Firebase Admin with proper error handling and configuration.
    
    Supports two modes:
    1. File-based: reads from serviceAccountKey.json (local development)
    2. Env-based: reads from FIREBASE_SERVICE_ACCOUNT_JSON env var (production/HF Spaces)
    """
    try:
        if not firebase_admin._apps:
            cred = None
            cred_path = settings.get_firebase_credentials_path()

            if os.path.exists(cred_path):
                # Local development: load from file
                cred = credentials.Certificate(cred_path)
                logger.info("Loading Firebase credentials from file")
            else:
                # Production: load from environment variable
                json_str = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
                if json_str:
                    service_account_info = json.loads(json_str)
                    cred = credentials.Certificate(service_account_info)
                    logger.info("Loading Firebase credentials from environment variable")
                else:
                    msg = f"Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_JSON env var or provide {cred_path} file."
                    logger.error(msg)
                    raise RuntimeError(msg)

            firebase_admin.initialize_app(cred, {
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET
            })
            logger.info("Firebase Admin initialized successfully")
    except Exception as e:
        logger.error("Error initializing Firebase Admin: %s", e)
        raise e
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

async def ensure_indexes():
    """Create database indexes using the centralized session manager."""
    logger.info("Ensuring database indexes...")
    database = db_manager.get_db()
    try:
        await database.courses.create_index("id", unique=True)
        await database.videos.create_index("id", unique=True)
        await database.videos.create_index("processing_status")
        await database.videos.create_index([("course_id", 1), ("processing_status", 1)])
        await database.processing_queue.create_index([("status", 1), ("priority", -1)])
        await database.processing_queue.create_index("video_id", unique=True)
        logger.info("Database indexes ensured successfully")
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"Error creating indexes: {e}", exc_info=True)
=======
        logger.error("Error creating indexes: %s", e)
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
