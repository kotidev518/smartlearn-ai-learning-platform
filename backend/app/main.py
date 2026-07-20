from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import asyncio
<<<<<<< HEAD
import logging
=======
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd

from .database import init_firebase, ensure_indexes
from .services.embedding_service import init_embedding_service
from .routers import auth, courses, analytics, recommendations, admin, vectors
from .services.processing_queue_service import processing_worker
from .core.config import settings
<<<<<<< HEAD
from .core.logging import setup_logging
from .core.middleware import CorrelationIDMiddleware, RequestLoggingMiddleware
from .db.session import db_manager

# Initialize Logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
=======
from .core.logger import setup_logging
from .db.session import db_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
    db_manager.init_db()
    init_firebase()
    init_embedding_service()  # Now initializes for lazy loading
    await ensure_indexes()
    
    yield
    
    # Shutdown
<<<<<<< HEAD
    logger.info("🛑 Shutting down background processes...")
    await processing_worker.stop_worker()
    await db_manager.close_db()


app = FastAPI(lifespan=lifespan)

# Add Middlewares (Ordered: outer to inner)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationIDMiddleware)

=======
    await db_manager.close_db()

app = FastAPI(lifespan=lifespan)

>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(vectors.router, prefix="/api")  # Vector search endpoints

@app.get("/")
async def root():
    return {"message": "Welcome to the Course Platform API"}
<<<<<<< HEAD
=======

@app.get("/api/debug-config")
async def debug_config():
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "database_name": settings.DB_NAME,
        "firebase_project": settings.FIREBASE_CREDENTIALS
    }
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
