from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_current_user, get_recommendation_service
from ..schemas import NextVideoRecommendation
from ..services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/next-video", response_model=NextVideoRecommendation)
async def get_next_video_recommendation(
    course_id: Optional[str] = None,
    user = Depends(get_current_user),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """AI-based recommendation using SBERT embeddings and mastery scores.
    
    If course_id is provided, recommendations are scoped to that course.
    Otherwise, the course is inferred from the user's most recently watched video.
    """
    recommendation = await recommendation_service.get_next_video_recommendation(user, course_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="No videos available")
    return recommendation
