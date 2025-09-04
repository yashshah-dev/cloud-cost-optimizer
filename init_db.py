#!/usr/bin/env python3
"""
Database initialization script for Cloud Cost Optimizer
Creates all database tables defined in the models
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import engine
from app.models import Base

async def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    return True

async def main():
    """Main function"""
    print("🚀 Initializing Cloud Cost Optimizer database...")
    success = await create_tables()
    if success:
        print("🎉 Database initialization completed!")
        return 0
    else:
        print("💥 Database initialization failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
