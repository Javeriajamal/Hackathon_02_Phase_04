#!/usr/bin/env python3
"""
Script to reset the database schema to match the current models
"""

import asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from database import AsyncSessionLocal
import os

# Import models to register them with SQLModel metadata
from models import *  # noqa: F401, F403

# Load the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://neondb_owner:npg_qkby1NLrfZ2V@ep-raspy-flower-ah5l2s9x-pooler.c-3.us-east-1.aws.neon.tech/neondb")

async def reset_database():
    """Drop and recreate all tables to match current models"""

    # Create async engine
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(SQLModel.metadata.drop_all)
        print("Dropped all existing tables")

        # Create all tables according to current models
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Created all tables according to current models")

    await engine.dispose()
    print("Database reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_database())