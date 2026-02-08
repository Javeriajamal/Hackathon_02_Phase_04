from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.auth import router as auth_router
from routers.tasks import router as tasks_router
from routers.chat import router as chat_router
import os
import logging
from contextlib import asynccontextmanager
from database import init_db
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app with lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown events."""
    logger.info("Starting up the application...")
    try:
        # Initialize database on startup
        await init_db()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    yield
    # Shutdown events can be added here if needed
    logger.info("Shutting down the application...")

app = FastAPI(
    title="Evolution of Todo - Phase 2 API",
    description="API for the Evolution of Todo project with authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

# Include the routers
logger.info("Including auth router with prefix /api/v1")
app.include_router(auth_router, prefix="/api/v1")   # auth_router has /auth prefix -> becomes /api/v1/auth

logger.info("Including tasks router with prefix /api/v1")
app.include_router(tasks_router, prefix="/api/v1")  # tasks_router has /tasks prefix -> becomes /api/v1/tasks

logger.info("Including chat router (already has /api/v1 prefix)")
app.include_router(chat_router)                    # chat_router already has /api/v1 prefix -> becomes /api/v1/chat

logger.info("All routers included successfully")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed - API is running")
    return {"message": "Evolution of Todo - Phase 2 API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Phase-2 API with Authentication"}

# Global exception handlers
@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    logger.warning(f"Not found error: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )