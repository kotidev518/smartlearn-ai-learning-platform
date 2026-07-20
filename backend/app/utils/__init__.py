from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
import bcrypt
from firebase_admin import storage
from ..config import settings
<<<<<<< HEAD
from ..core.logging import get_logger
=======
from ..core.logger import get_logger
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

logger = get_logger(__name__)

def get_video_url(url_or_path: str) -> str:
    """
    Transforms a stored video path into a usable URL.
    - If it's already a full URL (http/https), returns it as is.
    - If it's a gs:// URI, extracts the path.
    - If it's a storage path, generates a signed URL.
    """
    if not url_or_path:
        return ""
    
    if url_or_path.startswith(('http://', 'https://')):
        return url_or_path
    
    # Handle gs:// format
    blob_path = url_or_path
    if url_or_path.startswith('gs://'):
        # Format: gs://bucket-name/path/to/file
        try:
            parts = url_or_path.replace('gs://', '').split('/', 1)
            if len(parts) == 2:
                # We ignore the bucket part if we are using the default bucket
                blob_path = parts[1]
            else:
                return url_or_path
        except Exception:
            pass
            
    # Assume it's a path in Firebase Storage
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        return blob.generate_signed_url(expiration=timedelta(hours=1))
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"Error generating signed URL for {url_or_path}: {e}", exc_info=True)
=======
        logger.error("Error generating signed URL for %s: %s", url_or_path, e)
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
        return url_or_path

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
