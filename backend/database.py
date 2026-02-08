from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator
import os
import logging
from dotenv import load_dotenv

# Import models to register them with SQLModel metadata
try:
    from .models import *  # noqa: F401, F403
except ImportError:
    from models import *  # noqa: F401, F403

load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration for Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost/todo_db")

# For async engine, remove sslmode from URL if present since asyncpg handles SSL differently
ASYNC_DATABASE_URL = DATABASE_URL
if "sslmode=" in DATABASE_URL:
    # Remove sslmode from the URL for asyncpg compatibility
    import re
    ASYNC_DATABASE_URL = re.sub(r'[&?]sslmode=\w+', '', DATABASE_URL)
    # Add back just the base URL without sslmode
    if "?sslmode=" in DATABASE_URL:
        ASYNC_DATABASE_URL = DATABASE_URL.split("?sslmode=")[0]
    elif "&sslmode=" in DATABASE_URL:
        ASYNC_DATABASE_URL = DATABASE_URL.split("&sslmode=")[0]

# Async engine for async operations with connection pooling
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for debugging, False in production
    pool_size=20,  # Recommended pool size for Neon
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "server_settings": {
            "application_name": "evolution-of-todo-app"
        }
    }
)

# Session maker for async sessions
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        yield session


def get_session():
    """Synchronous session dependency for auth middleware and services"""
    from sqlmodel import Session
    sync_engine = get_sync_engine()
    with Session(sync_engine) as session:
        yield session


async def init_db():
    """Initialize the database with all tables and verify connectivity"""
    logger.info("Initializing database connection...")
    try:
        async with async_engine.begin() as conn:
            # Create all tables defined in SQLModel
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_sync_engine():
    """Get synchronous engine for migrations and sync operations"""
    sync_database_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    return create_engine(
        sync_database_url,
        echo=False,  # Set to True for debugging
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
            "application_name": "evolution-of-todo-app-sync"
        }
    )


async def test_db_connection():
    """Test database connectivity"""
    try:
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            # Test the connection by running a simple query
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            logger.info("Database connectivity test passed!")
            return True
    except Exception as e:
        logger.error(f"Database connectivity test failed: {e}")
        return False