import numpy as np
from typing import List, Dict, Tuple, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.embedding_service import embedding_service
from app.schemas import Video, NextVideoRecommendation
from app.utils import get_video_url
<<<<<<< HEAD
from app.core.logging import get_logger

logger = get_logger(__name__)
=======
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

class RecommendationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

<<<<<<< HEAD
    async def get_next_video_recommendation(
        self, user: dict, course_id: Optional[str] = None
    ) -> NextVideoRecommendation:
        """AI-based recommendation using SBERT embeddings and mastery scores.
        
        Recommendations are always scoped to a single course:
        - If course_id is provided, use it directly.
        - Otherwise, infer from the user's most recently watched video.
        """
        user_id = user['id']
        
        # Get user's mastery scores
        mastery_list = await self.db.mastery_scores.find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(1000)
        mastery_dict = {m['topic']: m['score'] for m in mastery_list}
        
        # Get user's progress
        progress_list = await self.db.user_progress.find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(1000)
        watched_videos = {p['video_id']: p for p in progress_list}
        
        # Determine the course_id to scope recommendations
        last_watched_video = None
        if progress_list:
            sorted_progress = sorted(
                progress_list, key=lambda x: x.get('timestamp', ''), reverse=True
            )
            if sorted_progress:
                last_watched_video = await self.db.videos.find_one(
                    {"id": sorted_progress[0]['video_id']}, {"_id": 0}
                )
        
        # If no course_id provided, infer from last watched video
        if not course_id and last_watched_video:
            course_id = last_watched_video.get('course_id')
        
        # Build the video query — scoped to course if we have one
        video_query = {}
        if course_id:
            video_query["course_id"] = course_id
        
        # Get videos (filtered by course)
        all_videos = await self.db.videos.find(
            video_query, {"_id": 0}
        ).sort("order", 1).to_list(1000)
        
        if not all_videos:
            return None
        
=======
    async def get_next_video_recommendation(self, user: dict) -> NextVideoRecommendation:
        """AI-based recommendation using SBERT embeddings and mastery scores"""
        user_id = user['id']
        
        # Get user's mastery scores
        mastery_list = await self.db.mastery_scores.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
        mastery_dict = {m['topic']: m['score'] for m in mastery_list}
        
        # Get user's progress
        progress_list = await self.db.user_progress.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
        watched_videos = {p['video_id']: p for p in progress_list}
        
        # Get all videos
        all_videos = await self.db.videos.find({}, {"_id": 0}).sort("order", 1).to_list(1000)
        if not all_videos:
            return None
        
        # Get user's last watched video for semantic similarity
        last_watched_video = None
        if progress_list:
            sorted_progress = sorted(progress_list, key=lambda x: x.get('timestamp', ''), reverse=True)
            if sorted_progress:
                last_watched_video = await self.db.videos.find_one({"id": sorted_progress[0]['video_id']}, {"_id": 0})
        
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
        # Calculate scores for each unwatched video
        candidate_videos = []
        for video in all_videos:
            video_id = video['id']
            if video_id in watched_videos and watched_videos[video_id].get('completed', False):
                continue
            
            if video_id in watched_videos and not watched_videos[video_id].get('completed', False):
                candidate_videos.append({
                    'video': video,
                    'score': 1000,
                    'reason': f"Continue watching '{video['title']}' ({watched_videos[video_id]['watch_percentage']:.0f}% completed)"
                })
                continue
            
<<<<<<< HEAD
            score, reason = await self._calculate_video_score(
                video, user, mastery_dict, last_watched_video
            )
=======
            score, reason = self._calculate_video_score(video, user, mastery_dict, last_watched_video)
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
            candidate_videos.append({'video': video, 'score': score, 'reason': reason})
        
        if not candidate_videos:
            recommended = all_videos[0]
            reason = "Congratulations! Review from the beginning"
        else:
            candidate_videos.sort(key=lambda x: x['score'], reverse=True)
            best = candidate_videos[0]
            recommended = best['video']
            reason = best['reason']
        
        recommended_video = Video(**recommended)
        if hasattr(recommended_video, 'url'):
            recommended_video.url = get_video_url(recommended_video.url)

        return NextVideoRecommendation(
            video=recommended_video,
            reason=reason,
            mastery_scores=mastery_dict
        )

<<<<<<< HEAD
    async def _calculate_video_score(
        self, video: dict, user: dict, mastery_dict: dict, last_watched: Optional[dict]
    ) -> Tuple[float, str]:
=======
    def _calculate_video_score(self, video: dict, user: dict, mastery_dict: dict, last_watched: Optional[dict]) -> Tuple[float, str]:
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
        score = 0
        reasons = []
        
        # 1. Mastery-based scoring (40% weight)
        video_topics = video.get('topics', [])
        if video_topics and mastery_dict:
            topic_scores = [mastery_dict.get(topic, 0) for topic in video_topics]
            avg_mastery = sum(topic_scores) / len(topic_scores) if topic_scores else 0
            if 40 <= avg_mastery <= 70:
                score += 40
                reasons.append(f"Optimal challenge level for {video_topics[0]}")
            elif avg_mastery < 40:
                score += 30
                reasons.append(f"Build foundation in {video_topics[0]}")
            else:
                score += 20
        else:
            if video['difficulty'] == user.get('initial_level', 'Easy'):
                score += 35
                reasons.append(f"Matches your {user.get('initial_level', 'Easy')} level")
        
        # 2. Difficulty progression (20% weight)
        difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        user_level = difficulty_map.get(user.get('initial_level', 'Easy'), 2)
        video_level = difficulty_map.get(video['difficulty'], 2)
        if video_level == user_level: score += 20
        elif video_level == user_level + 1:
            score += 15
            reasons.append("Next difficulty level")
        
<<<<<<< HEAD
        # 3. SBERT Semantic similarity (30% weight)
        if last_watched and embedding_service:
            similarity = await self._compute_sbert_similarity(last_watched, video)
            if similarity is not None:
                # Scale similarity (0 to 1) → 0 to 30 points
                sim_score = similarity * 30
                score += sim_score
                if similarity > 0.5:
                    reasons.append(f"Semantically related (similarity: {similarity:.2f})")
=======
        # 3. Semantic similarity (30% weight) - Simplified here, should ideally use a cached embedding
        if last_watched and embedding_service:
            # Note: In a real app, embeddings should be pre-calculated and stored in DB
            pass # Skipping on-the-fly encoding for performance in service
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
        
        # 4. Sequential ordering (10% weight)
        if video.get('order', 0) < 10:
            score += 10 - video.get('order', 0)
        
<<<<<<< HEAD
        return score, (reasons[0] if reasons else f"Learn {video['title']}")

    async def _compute_sbert_similarity(
        self, source_video: dict, target_video: dict
    ) -> Optional[float]:
        """Compute SBERT cosine similarity between two videos using pre-computed embeddings."""
        try:
            source_embedding = source_video.get('embedding')
            target_embedding = target_video.get('embedding')
            
            if not source_embedding or not target_embedding:
                return None
            
            similarity = await embedding_service.compute_cosine_similarity(
                source_embedding, target_embedding
            )
            return similarity
        except Exception as e:
            logger.warning(f"Failed to compute SBERT similarity: {e}")
            return None
=======
        # 5. Course consistency
        if last_watched and video['course_id'] == last_watched['course_id']:
            score += 100
            reasons.append(f"Continue in '{last_watched.get('course_id', 'this course')}'")
        
        return score, (reasons[0] if reasons else f"Learn {video['title']}")
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
