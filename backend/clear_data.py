#!/usr/bin/env python3
"""
Database cleanup script for Cloud Cost Optimizer
Clears all sample data from the database
"""

import asyncio
import sys

from app.database import async_session_maker
from app.models import CloudResource, CostEntry, OptimizationRecommendation, OptimizationExecution, User, AuditLog

async def clear_sample_data():
    """Clear all data from database tables"""
    try:
        print("🧹 Clearing sample data...")

        async with async_session_maker() as session:
            # Delete in reverse order due to foreign key constraints
            await session.execute(AuditLog.__table__.delete())
            await session.execute(OptimizationExecution.__table__.delete())
            await session.execute(OptimizationRecommendation.__table__.delete())
            await session.execute(CostEntry.__table__.delete())
            await session.execute(CloudResource.__table__.delete())
            await session.execute(User.__table__.delete())
            await session.commit()

        print("✅ Sample data cleared successfully!")
        return True

    except Exception as e:
        print(f"❌ Error clearing sample data: {e}")
        return False

async def main():
    """Main function"""
    success = await clear_sample_data()
    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
