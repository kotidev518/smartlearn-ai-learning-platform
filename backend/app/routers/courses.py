from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from ..database import db
from ..schemas import Course, Video, VideoProgressUpdate, Quiz, QuizSubmission, QuizResult
from ..dependencies import get_current_user
from ..utils import get_video_url
from ..services import update_mastery_scores_for_video

router = APIRouter(tags=["courses"])

# ==================== Course Routes ====================

@router.get("/courses", response_model=List[Course])
async def get_courses(user = Depends(get_current_user)):
    courses = await db.courses.find({}, {"_id": 0}).to_list(1000)
    return courses

@router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str, user = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# ==================== Video Routes ====================

@router.get("/videos", response_model=List[Video])
async def get_videos(course_id: Optional[str] = None, user = Depends(get_current_user)):
    query = {"course_id": course_id} if course_id else {}
    videos = await db.videos.find(query, {"_id": 0}).sort("order", 1).to_list(1000)
    
    # Process URLs
    for video in videos:
        if 'url' in video:
            video['url'] = get_video_url(video['url'])
            
    return videos

@router.get("/videos/{video_id}", response_model=Video)
async def get_video(video_id: str, user = Depends(get_current_user)):
    video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if 'url' in video:
        video['url'] = get_video_url(video['url'])
        
    return video

@router.post("/videos/{video_id}/progress")
async def update_video_progress(video_id: str, progress_data: VideoProgressUpdate, user = Depends(get_current_user)):
    progress_doc = {
        "user_id": user['id'],
        "video_id": video_id,
        "watch_percentage": progress_data.watch_percentage,
        "completed": progress_data.completed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_progress.update_one(
        {"user_id": user['id'], "video_id": video_id},
        {"$set": progress_doc},
        upsert=True
    )
    
    # Update mastery scores if completed
    if progress_data.completed:
        video = await db.videos.find_one({"id": video_id}, {"_id": 0})
        if video:
            await update_mastery_scores_for_video(user['id'], video, score=80.0)  # Base score
    
    return {"success": True}

@router.get("/videos/{video_id}/progress")
async def get_video_progress(video_id: str, user = Depends(get_current_user)):
    progress = await db.user_progress.find_one(
        {"user_id": user['id'], "video_id": video_id},
        {"_id": 0}
    )
    return progress if progress else {"watch_percentage": 0, "completed": False}

# ==================== Quiz Routes ====================

@router.get("/quizzes/{video_id}", response_model=Quiz)
async def get_quiz(video_id: str, user = Depends(get_current_user)):
    quiz = await db.quizzes.find_one({"video_id": video_id}, {"_id": 0})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/quizzes/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission, user = Depends(get_current_user)):
    quiz = await db.quizzes.find_one({"id": submission.quiz_id}, {"_id": 0})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    correct = 0
    for i, answer in enumerate(submission.answers):
        if i < len(quiz['questions']) and answer == quiz['questions'][i]['correct_answer']:
            correct += 1
    
    score = (correct / len(quiz['questions'])) * 100 if quiz['questions'] else 0
    
    # Save result
    result_id = str(uuid4())
    result_doc = {
        "id": result_id,
        "user_id": user['id'],
        "quiz_id": submission.quiz_id,
        "video_id": quiz['video_id'],
        "score": score,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.quiz_results.insert_one(result_doc)
    
    # Update mastery scores based on quiz performance
    video = await db.videos.find_one({"id": quiz['video_id']}, {"_id": 0})
    if video:
        # Use update_mastery_scores_for_video from services
        await update_mastery_scores_for_video(user['id'], video, score)
    
    return QuizResult(**result_doc)

@router.post("/init-data")
async def initialize_data(force: bool = False):
    """Initialize sample courses and videos with stable IDs"""
    # Check if data exists
    if force:
        print("Forced re-initialization: clearing existing data...")
        await db.courses.delete_many({})
        await db.videos.delete_many({})
        await db.quizzes.delete_many({})
    else:
        existing = await db.courses.count_documents({})
        if existing > 0:
            return {"message": "Data already initialized. Use force=true to override."}
    
    # Sample courses with stable IDs
    courses_data = [
        {
            "id": "course-1",
            "title": "Python Programming Fundamentals",
            "description": "Master the basics of Python programming",
            "difficulty": "Easy",
            "topics": ["Python", "Programming", "Variables", "Functions"],
            "thumbnail": "https://images.unsplash.com/photo-1753998943619-b9cd910887e5?crop=entropy&cs=srgb&fm=jpg&q=85",
            "video_count": 4
        },
        {
            "id": "course-2",
            "title": "Data Science with Python",
            "description": "Learn data analysis and visualization",
            "difficulty": "Medium",
            "topics": ["Data Science", "Python", "Pandas", "Visualization"],
            "thumbnail": "https://images.unsplash.com/photo-1744782211816-c5224434614f?crop=entropy&cs=srgb&fm=jpg&q=85",
            "video_count": 4
        },
        {
            "id": "course-3",
            "title": "Machine Learning Advanced",
            "description": "Deep dive into ML algorithms",
            "difficulty": "Hard",
            "topics": ["Machine Learning", "Algorithms", "Neural Networks"],
            "thumbnail": "https://images.unsplash.com/photo-1764336312138-14a5368a6cd3?crop=entropy&cs=srgb&fm=jpg&q=85",
            "video_count": 3
        }
    ]
    
    await db.courses.insert_many(courses_data)
    
    # Sample videos with stable IDs
    videos_data = [
        # Course 1: Python Fundamentals
        {
            "id": "vid-python-1",
            "course_id": "course-1",
            "title": "Introduction to Python",
            "description": "Learn Python basics and syntax",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/01. Big O Intro.mp4",
            "duration": 600,
            "difficulty": "Easy",
            "topics": ["Python", "Programming"],
            "transcript": "Python is a high-level programming language. It is easy to learn and powerful for various applications.",
            "order": 1
        },
        {
            "id": "vid-python-2",
            "course_id": "course-1",
            "title": "Variables and Data Types",
            "description": "Understanding Python variables",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/02. Big O Worst Case.mp4",
            "duration": 480,
            "difficulty": "Easy",
            "topics": ["Python", "Variables"],
            "transcript": "Variables in Python store data values. Python has various data types including integers, strings, and lists.",
            "order": 2
        },
        {
            "id": "vid-python-3",
            "course_id": "course-1",
            "title": "Functions and Methods",
            "description": "Creating reusable code with functions",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/03. Big O O(n).mp4",
            "duration": 720,
            "difficulty": "Easy",
            "topics": ["Python", "Functions"],
            "transcript": "Functions are reusable blocks of code. They help organize your program and make it more maintainable.",
            "order": 3
        },
        {
            "id": "vid-python-4",
            "course_id": "course-1",
            "title": "Control Flow and Loops",
            "description": "Master if statements and loops",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/04. Big O Drop Constants.mp4",
            "duration": 540,
            "difficulty": "Easy",
            "topics": ["Python", "Programming"],
            "transcript": "Control flow statements like if-else and loops like for and while help control program execution.",
            "order": 4
        },
        # Course 2: Data Science
        {
            "id": "vid-ds-1",
            "course_id": "course-2",
            "title": "Introduction to Data Science",
            "description": "Overview of data science concepts",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/05. Big O O(n^2).mp4",
            "duration": 660,
            "difficulty": "Medium",
            "topics": ["Data Science", "Python"],
            "transcript": "Data science involves drawing insights from data using scientific methods, processes, algorithms, and systems.",
            "order": 1
        },
        {
            "id": "vid-ds-2",
            "course_id": "course-2",
            "title": "Pandas for Data Manipulation",
            "description": "Working with DataFrames",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/06. Big O O(1).mp4",
            "duration": 900,
            "difficulty": "Medium",
            "topics": ["Pandas", "Python", "Data Science"],
            "transcript": "Pandas is a software library written for the Python programming language for data manipulation and analysis.",
            "order": 2
        },
        {
            "id": "vid-ds-3",
            "course_id": "course-2",
            "title": "Data Visualization with Matplotlib",
            "description": "Creating plots and charts",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/07. Big O O(log n).mp4",
            "duration": 780,
            "difficulty": "Medium",
            "topics": ["Visualization", "Python"],
            "transcript": "Matplotlib is a plotting library for the Python programming language and its numerical mathematics extension NumPy.",
            "order": 3
        },
        {
            "id": "vid-ds-4",
            "course_id": "course-2",
            "title": "Exploratory Data Analysis",
            "description": "Analyzing datasets",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/08. Big O Arrays.mp4",
            "duration": 840,
            "difficulty": "Medium",
            "topics": ["Data Science", "Analysis"],
            "transcript": "Exploratory Data Analysis (EDA) is an approach to analyzing data sets to summarize their main characteristics.",
            "order": 4
        },
        # Course 3: Machine Learning
        {
            "id": "vid-ml-1",
            "course_id": "course-3",
            "title": "Supervised Learning",
            "description": "Regression and Classification",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/09. Lists.mp4",
            "duration": 960,
            "difficulty": "Hard",
            "topics": ["Machine Learning", "Algorithms"],
            "transcript": "Supervised learning is the machine learning task of learning a function that maps an input to an output based on example input-output pairs.",
            "order": 1
        },
        {
            "id": "vid-ml-2",
            "course_id": "course-3",
            "title": "Neural Networks Basics",
            "description": "Understanding Perceptrons",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/11. Classes & Pointers.mp4",
            "duration": 1020,
            "difficulty": "Hard",
            "topics": ["Neural Networks", "Deep Learning"],
            "transcript": "Artificial neural networks are computing systems inspired by the biological neural networks that constitute animal brains.",
            "order": 2
        },
        {
            "id": "vid-ml-3",
            "course_id": "course-3",
            "title": "Model Evaluation",
            "description": "Metrics and Validation",
            "url": "gs://online-course-platform-68c2c.firebasestorage.app/DSA/102. Binary Search Tree Intro.mp4",
            "duration": 600,
            "difficulty": "Hard",
            "topics": ["Machine Learning", "Analysis"],
            "transcript": "Model evaluation is an integral part of the model development process. It helps to find the best model that represents our data.",
            "order": 3
        }
    ]
    
    await db.videos.insert_many(videos_data)
    
    # Sample quizzes (1 per video)
    quizzes_data = []
    
    for video in videos_data:
        quizzes_data.append({
            "id": f"quiz-{video['id']}",
            "video_id": video['id'],
            "questions": [
                {
                    "question": f"What is the main topic of {video['title']}?",
                    "options": [
                        f"{video['topics'][0]}",
                        "Cooking",
                        "History",
                        "Music"
                    ],
                    "correct_answer": 0
                },
                {
                    "question": "Which of the following is true regarding the content?",
                    "options": [
                        "It is unrelated to the course",
                        "It covers advanced topics only",
                        f"It discusses {video['description']}",
                        "None of the above"
                    ],
                    "correct_answer": 2
                },
                {
                    "question": "What is the difficulty level of this video?",
                    "options": [
                        "Impossible",
                        video['difficulty'],
                        "Very Easy",
                        "Expert"
                    ],
                    "correct_answer": 1
                },
                {
                    "question": "Which concept was mentioned in the transcript?",
                    "options": [
                        "Quantum Physics",
                        "Blockchain",
                        video['topics'][0] if video['topics'] else "General",
                        "Augmented Reality"
                    ],
                    "correct_answer": 2
                }
            ]
        })
        
    await db.quizzes.insert_many(quizzes_data)
    
    return {"message": "Data initialized successfully", "counts": {
        "courses": len(courses_data),
        "videos": len(videos_data),
        "quizzes": len(quizzes_data)
    }}
