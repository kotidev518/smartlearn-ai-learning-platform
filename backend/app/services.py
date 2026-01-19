from datetime import datetime, timezone
from .database import db

async def update_mastery_scores_for_video(user_id: str, video: dict, score: float):
    """Update mastery scores for all topics in a video"""
    for topic in video.get('topics', []):
        # Get current mastery
        current = await db.mastery_scores.find_one(
            {"user_id": user_id, "topic": topic},
            {"_id": 0}
        )
        
        if current:
            # Weighted average: 70% old, 30% new
            new_score = (current['score'] * 0.7) + (score * 0.3)
        else:
            new_score = score * 0.8  # Start at 80% of quiz score
        
        await db.mastery_scores.update_one(
            {"user_id": user_id, "topic": topic},
            {"$set": {
                "user_id": user_id,
                "topic": topic,
                "score": new_score,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
