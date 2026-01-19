from typing import List
from fastapi import APIRouter, Depends

from ..database import db
from ..schemas import MasteryScore
from ..dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/mastery", response_model=List[MasteryScore])
async def get_mastery_scores(user = Depends(get_current_user)):
    scores = await db.mastery_scores.find({"user_id": user['id']}, {"_id": 0}).to_list(1000)
    return scores

@router.get("/progress")
async def get_overall_progress(user = Depends(get_current_user)):
    # Get all progress
    progress_list = await db.user_progress.find({"user_id": user['id']}, {"_id": 0}).to_list(1000)
    
    total_videos = await db.videos.count_documents({})
    completed_videos = sum(1 for p in progress_list if p.get('completed', False))
    
    # Get quiz results
    quiz_results = await db.quiz_results.find({"user_id": user['id']}, {"_id": 0}).to_list(1000)
    avg_quiz_score = sum(r['score'] for r in quiz_results) / len(quiz_results) if quiz_results else 0
    
    return {
        "total_videos": total_videos,
        "completed_videos": completed_videos,
        "completion_percentage": (completed_videos / total_videos * 100) if total_videos > 0 else 0,
        "average_quiz_score": avg_quiz_score,
        "total_quizzes": len(quiz_results)
    }
