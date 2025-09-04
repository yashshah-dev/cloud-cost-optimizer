#!/usr/bin/env python3
"""
Load Synthetic Data into Database

This script loads the realistic synthetic data into the PostgreSQL database
for use by the Cloud Cost Optimizer application.
"""

import asyncio
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from database import engine, async_session_maker, settings
from models import CloudResource, CostEntry, Base


class DatabaseLoader:
    """Load synthetic data into the database"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from a JSON file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Synthetic data file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def create_tables(self):
        """Create all database tables"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/verified")

    async def clear_existing_data(self, session: AsyncSession):
        """Clear existing synthetic data (optional)"""
        print("🧹 Clearing existing data...")

        # Delete in correct order due to foreign keys
        await session.execute(text("DELETE FROM cost_entries"))
        await session.execute(text("DELETE FROM optimization_recommendations"))
        await session.execute(text("DELETE FROM optimization_executions"))
        await session.execute(text("DELETE FROM cloud_resources"))

        await session.commit()
        print("✅ Existing data cleared")

    async def load_resources(self, session: AsyncSession, filename: str) -> Dict[str, CloudResource]:
        """Load resources into database and return mapping"""
        print(f"📥 Loading resources from {filename}...")

        resources_data = self.load_json(filename)
        resource_map = {}

        for resource_data in resources_data:
            # Map the resource type from the synthetic data to the standardized enum value
            mapped_resource_type = self._map_resource_type(resource_data.get('resource_type', 'other'))

            # Create database resource object
            db_resource = CloudResource(
                id=resource_data['resource_id'],
                provider=resource_data['provider'],
                resource_id=resource_data['resource_id'],
                resource_type=mapped_resource_type,
                name=resource_data.get('name', ''),
                region=resource_data.get('region', ''),
                tags=resource_data.get('tags', {}),
                specifications=resource_data.get('specifications', {}),
                created_at=datetime.fromisoformat(resource_data['created_at']) if 'created_at' in resource_data else datetime.now(),
                updated_at=datetime.fromisoformat(resource_data['updated_at']) if 'updated_at' in resource_data else datetime.now()
            )

            session.add(db_resource)
            resource_map[str(resource_data['resource_id'])] = db_resource

        await session.commit()
        print(f"✅ Loaded {len(resources_data)} resources")
        return resource_map

    async def load_cost_entries(self, session: AsyncSession, filename: str, resource_map: Dict[str, CloudResource]):
        """Load cost entries into database"""
        print(f"📥 Loading cost entries from {filename}...")

        cost_entries_data = self.load_json(filename)
        batch_size = 1000

        for i in range(0, len(cost_entries_data), batch_size):
            batch = cost_entries_data[i:i + batch_size]

            for cost_data in batch:
                # Find the corresponding resource
                resource = resource_map.get(str(cost_data['resource_id']))
                if not resource:
                    print(f"⚠️  Warning: Resource {cost_data['resource_id']} not found, skipping cost entry")
                    continue

                # Create database cost entry
                db_cost_entry = CostEntry(
                    id=str(uuid.uuid4()),  # Generate unique ID since JSON doesn't have one
                    resource_id=resource.id,
                    date=datetime.fromisoformat(cost_data['date']) if isinstance(cost_data['date'], str) else cost_data['date'],
                    cost=cost_data['cost'],
                    currency=cost_data.get('currency', 'USD'),
                    service_name=cost_data.get('service', 'unknown'),
                    cost_category=self._map_resource_type(cost_data.get('service', 'other'))
                )

                session.add(db_cost_entry)

            await session.commit()
            print(f"✅ Loaded batch {i//batch_size + 1} ({len(batch)} cost entries)")

        print(f"✅ Loaded {len(cost_entries_data)} total cost entries")

    def _map_resource_type(self, resource_type_str: str) -> str:
        """Map provider-specific resource type names to standardized enum values"""
        resource_type_lower = resource_type_str.lower()

        # Provider-specific mappings
        if resource_type_lower in ['rds', 'mysql', 'postgres', 'sql', 'database']:
            return 'database'
        elif resource_type_lower in ['lambda', 'function', 'serverless']:
            return 'serverless'
        elif resource_type_lower in ['ec2', 'vm', 'compute', 'instance']:
            return 'compute'
        elif resource_type_lower in ['s3', 'storage', 'bucket']:
            return 'storage'
        elif resource_type_lower in ['vpc', 'network', 'loadbalancer', 'lb']:
            return 'network'
        elif resource_type_lower in ['ecs', 'container', 'docker', 'kubernetes', 'k8s']:
            return 'container'
        else:
            return 'other'

    async def load_balanced_scenario(self, session: AsyncSession, clear_existing: bool = True):
        """Load the complete balanced scenario"""
        print("🚀 Loading Balanced Multi-Cloud Scenario into Database")
        print("=" * 60)

        if clear_existing:
            await self.clear_existing_data(session)

        # Load resources first
        resource_map = await self.load_resources(session, "balanced_resources.json")

        # Load cost entries
        await self.load_cost_entries(session, "balanced_cost_entries.json", resource_map)

        print("✅ Balanced scenario loaded successfully!")

    async def load_provider_specific_data(self, session: AsyncSession, provider: str):
        """Load provider-specific data"""
        print(f"🚀 Loading {provider.upper()} Provider Data into Database")
        print("=" * 60)

        # Load resources
        resource_map = await self.load_resources(session, f"{provider}_resources.json")

        # Load cost entries
        await self.load_cost_entries(session, f"{provider}_cost_entries.json", resource_map)

        print(f"✅ {provider.upper()} data loaded successfully!")

    async def verify_data_loaded(self, session: AsyncSession):
        """Verify that data was loaded correctly"""
        print("\n🔍 Verifying Data Load")
        print("=" * 30)

        # Count resources
        result = await session.execute(text("SELECT COUNT(*) FROM cloud_resources"))
        resource_count = result.scalar()
        print(f"📊 Total Resources: {resource_count}")

        # Count cost entries
        result = await session.execute(text("SELECT COUNT(*) FROM cost_entries"))
        cost_count = result.scalar()
        print(f"💰 Total Cost Entries: {cost_count}")

        # Provider breakdown
        result = await session.execute(text("""
            SELECT provider, COUNT(*) as count
            FROM cloud_resources
            GROUP BY provider
            ORDER BY count DESC
        """))
        provider_counts = result.fetchall()

        print("🌐 Resources by Provider:")
        for provider, count in provider_counts:
            print(f"   {provider.upper()}: {count}")

        # Cost summary
        result = await session.execute(text("""
            SELECT
                SUM(cost) as total_cost,
                AVG(cost) as avg_daily_cost,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM cost_entries
        """))
        cost_summary = result.first()

        if cost_summary:
            print("\n💵 Cost Summary:")
            print(f"   Total Cost: ${cost_summary.total_cost:.2f}")
            print(f"   Average Daily Cost: ${cost_summary.avg_daily_cost:.2f}")
            print(f"   Date Range: {cost_summary.earliest_date.date()} to {cost_summary.latest_date.date()}")

        print("✅ Data verification complete!")


async def main():
    """Main function to load synthetic data into database"""
    print("🚀 Cloud Cost Optimizer - Database Synthetic Data Loader")
    print("=" * 65)

    # Check database connection
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and DATABASE_URL is set correctly")
        return 1

    # Set up data directory
    data_dir = Path(__file__).parent / "synthetic_data" / "datasets"
    if not data_dir.exists():
        print(f"❌ Synthetic data directory not found: {data_dir}")
        return 1

    loader = DatabaseLoader(data_dir)

    # Create tables if they don't exist
    await loader.create_tables()

    async with async_session_maker() as session:
        try:
            # Load balanced scenario
            await loader.load_balanced_scenario(session, clear_existing=True)

            # Optionally load provider-specific data
            print("\n" + "=" * 65)
            print("🔄 Loading Additional Provider Data...")

            for provider in ["aws", "gcp", "azure"]:
                try:
                    await loader.load_provider_specific_data(session, provider)
                except FileNotFoundError:
                    print(f"⚠️  {provider.upper()} data files not found, skipping...")

            # Verify the data load
            await loader.verify_data_loaded(session)

            print("\n" + "=" * 65)
            print("🎉 Synthetic data successfully loaded into database!")
            print("\n📊 Database is now populated with realistic test data for:")
            print("   • Multi-cloud resource inventory")
            print("   • Historical cost data with time series")
            print("   • Usage patterns and cost analysis")
            print("   • Optimization algorithm testing")
            print("\n🔧 Your Cloud Cost Optimizer is ready for development!")

        except Exception as e:
            print(f"\n❌ Error loading data: {e}")
            await session.rollback()
            return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
