#!/usr/bin/env python3
"""
Script to initialize the database tables
"""

import asyncio
from database import init_db

async def main():
    print("Initializing database...")
    try:
        await init_db()
        print("Database initialized successfully!")
        print("Tables created: users, tasks, conversations, messages")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Make sure your PostgreSQL server is running and the DATABASE_URL is correct.")

if __name__ == "__main__":
    asyncio.run(main())