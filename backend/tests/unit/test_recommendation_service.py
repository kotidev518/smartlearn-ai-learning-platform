import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import numpy as np
from bson.binary import Binary

from mongomock_motor import AsyncMongoMockClient
from app.services.recommendation_service import RecommendationService


def _make_embedding(seed: int = 42) -> bytes:
    """Create a fake 384-dim embedding binary (matching all-MiniLM-L6-v2 dimensions)."""
    rng = np.random.RandomState(seed)
    vec = rng.randn(384).astype(np.float32)
    vec = vec / np.linalg.norm(vec)  # normalize
    return Binary(vec.tobytes())


def _make_video(video_id: str, course_id: str, order: int, difficulty: str = "Easy",
                topics: list = None, embedding=None) -> dict:
    return {
        "id": video_id,
        "course_id": course_id,
        "title": f"Video {video_id}",
        "description": f"Description for {video_id}",
        "url": f"https://youtube.com/watch?v={video_id}",
        "youtube_id": video_id,
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/default.jpg",
        "duration": 600,
        "difficulty": difficulty,
        "topics": topics or ["python"],
        "transcript": "Sample transcript",
        "order": order,
        "embedding": embedding,
    }


@pytest.fixture
def db():
    client = AsyncMongoMockClient()
    return client.test_recommendation_db


@pytest.fixture
def user():
    return {
        "id": "user_1",
        "email": "test@example.com",
        "name": "Test User",
        "initial_level": "Easy",
        "role": "student",
    }


class TestRecommendationServiceCourseFilter:
    """Test that recommendations are scoped to a single course."""

    @pytest.mark.asyncio
    async def test_only_same_course_videos_returned(self, db, user):
        """When course_id is provided, only videos from that course should be candidates."""
        db_instance = db

        # Insert videos from two courses
        await db_instance.videos.insert_many([
            _make_video("v1", "course_A", 1),
            _make_video("v2", "course_A", 2),
            _make_video("v3", "course_B", 1),
            _make_video("v4", "course_B", 2),
        ])

        service = RecommendationService(db_instance)

        # Request recommendation for course_A
        with patch('app.services.recommendation_service.get_video_url', side_effect=lambda x: x):
            rec = await service.get_next_video_recommendation(user, course_id="course_A")

        assert rec is not None
        assert rec.video.course_id == "course_A"

    @pytest.mark.asyncio
    async def test_course_inferred_from_last_watched(self, db, user):
        """When no course_id is given, it should be inferred from the last watched video."""
        db_instance = db

        await db_instance.videos.insert_many([
            _make_video("v1", "course_A", 1),
            _make_video("v2", "course_A", 2),
            _make_video("v3", "course_B", 1),
        ])
        # User last watched a video from course_A
        await db_instance.user_progress.insert_one({
            "user_id": "user_1",
            "video_id": "v1",
            "watch_percentage": 100,
            "completed": True,
            "timestamp": "2026-02-28T10:00:00"
        })

        service = RecommendationService(db_instance)
        with patch('app.services.recommendation_service.get_video_url', side_effect=lambda x: x):
            rec = await service.get_next_video_recommendation(user, course_id=None)

        assert rec is not None
        # Should recommend from course_A (inferred), not course_B
        assert rec.video.course_id == "course_A"

    @pytest.mark.asyncio
    async def test_incomplete_video_prioritized(self, db, user):
        """An incomplete video in the same course should be top priority (score 1000)."""
        db_instance = db

        await db_instance.videos.insert_many([
            _make_video("v1", "course_A", 1),
            _make_video("v2", "course_A", 2),
        ])
        await db_instance.user_progress.insert_one({
            "user_id": "user_1",
            "video_id": "v1",
            "watch_percentage": 45,
            "completed": False,
            "timestamp": "2026-02-28T10:00:00"
        })

        service = RecommendationService(db_instance)
        with patch('app.services.recommendation_service.get_video_url', side_effect=lambda x: x):
            rec = await service.get_next_video_recommendation(user, course_id="course_A")

        assert rec is not None
        assert rec.video.id == "v1"
        assert "Continue watching" in rec.reason


class TestSBERTSimilarityScoring:
    """Test that SBERT embeddings are used for semantic similarity scoring."""

    @pytest.mark.asyncio
    async def test_sbert_similarity_used_when_embeddings_exist(self, db, user):
        """When both videos have embeddings, cosine similarity should contribute to score."""
        db_instance = db

        emb1 = _make_embedding(seed=42)
        emb2 = _make_embedding(seed=42)  # Same seed = identical embedding = similarity ≈ 1.0
        emb3 = _make_embedding(seed=99)  # Different seed = lower similarity

        await db_instance.videos.insert_many([
            _make_video("v1", "course_A", 1, embedding=emb1),
            _make_video("v2", "course_A", 2, embedding=emb2),
            _make_video("v3", "course_A", 3, embedding=emb3),
        ])
        # Mark v1 as watched so last_watched is set
        await db_instance.user_progress.insert_one({
            "user_id": "user_1",
            "video_id": "v1",
            "watch_percentage": 100,
            "completed": True,
            "timestamp": "2026-02-28T10:00:00"
        })

        service = RecommendationService(db_instance)
        with patch('app.services.recommendation_service.get_video_url', side_effect=lambda x: x):
            rec = await service.get_next_video_recommendation(user, course_id="course_A")

        assert rec is not None
        # v2 (identical embedding to v1) should score higher than v3
        assert rec.video.id == "v2"

    @pytest.mark.asyncio
    async def test_graceful_fallback_without_embeddings(self, db, user):
        """When no embeddings exist, recommendation should still work using other scoring factors."""
        db_instance = db

        # Videos without embeddings
        await db_instance.videos.insert_many([
            _make_video("v1", "course_A", 1),
            _make_video("v2", "course_A", 2),
        ])

        service = RecommendationService(db_instance)
        with patch('app.services.recommendation_service.get_video_url', side_effect=lambda x: x):
            rec = await service.get_next_video_recommendation(user, course_id="course_A")

        # Should still return a recommendation
        assert rec is not None
        assert rec.video.course_id == "course_A"

    @pytest.mark.asyncio 
    async def test_no_videos_returns_none(self, db, user):
        """When no videos exist for the given course, should return None."""
        db_instance = db

        service = RecommendationService(db_instance)
        rec = await service.get_next_video_recommendation(user, course_id="nonexistent_course")

        assert rec is None
