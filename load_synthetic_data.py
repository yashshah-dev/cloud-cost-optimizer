#!/usr/bin/env python3
"""
Load Synthetic Data into Database

This script loads the pre-generated synthetic data from JSON files
into the PostgreSQL database for testing the ML pipeline.
"""

import asyncio
import json
import os
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import async_session_maker, settings
from backend.app.models import Base, CloudResource, CostEntry

class SyntheticDataLoader:
    """Load synthetic data from JSON files into database."""

    def __init__(self):
        self.engine = create_async_engine(settings.database_url)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.data_dir = Path("/Users/yash/Documents/Freelance/projects/proposal-agent/backend/app/synthetic_data/datasets")

    def generate_synthetic_data(self):
        """Generate synthetic cloud cost data with optimization opportunities."""
        print("🔄 Generating synthetic data with optimization patterns...")

        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Generate resources with specific optimization patterns
        resources = []
        cost_entries = []

        # Create resources that will trigger different optimizations
        optimization_scenarios = [
            # Rightsizing down (low utilization)
            {"count": 8, "pattern": "low_utilization", "instance_type": "t3.large", "avg_cpu": 15, "cost_multiplier": 1.0},
            # Rightsizing up (high utilization) 
            {"count": 3, "pattern": "high_utilization", "instance_type": "t3.small", "avg_cpu": 85, "cost_multiplier": 1.0},
            # Reserved instance candidates (consistent usage)
            {"count": 5, "pattern": "consistent_usage", "instance_type": "m5.large", "avg_cpu": 60, "cost_multiplier": 1.0},
            # Spot instance candidates (moderate utilization)
            {"count": 4, "pattern": "spot_candidate", "instance_type": "c5.large", "avg_cpu": 45, "cost_multiplier": 1.0},
            # Storage optimization (underutilized storage)
            {"count": 6, "pattern": "storage_waste", "instance_type": "storage", "avg_cpu": 5, "cost_multiplier": 1.0},
            # Unused resources
            {"count": 4, "pattern": "unused", "instance_type": "t3.medium", "avg_cpu": 3, "cost_multiplier": 1.0},
        ]

        resource_id = 1
        providers = ['aws', 'gcp', 'azure']
        regions = {
            'aws': ['us-east-1', 'us-west-2', 'eu-west-1'],
            'gcp': ['us-central1', 'europe-west1'],
            'azure': ['East US', 'West Europe']
        }

        for scenario in optimization_scenarios:
            for i in range(scenario["count"]):
                provider = random.choice(providers)
                region = random.choice(regions[provider])
                
                # Create resource
                resource = {
                    'resource_id': str(uuid.uuid4()),
                    'name': f'{scenario["pattern"]}-{resource_id:03d}',
                    'resource_type': 'storage' if scenario["pattern"] == "storage_waste" else random.choice(['ec2', 'rds', 'lambda']),
                    'provider': provider,
                    'region': region,
                    'tags': {'Environment': 'prod' if random.random() > 0.3 else 'dev', 'Team': 'engineering'},
                    'specifications': {'instance_type': scenario["instance_type"]},
                    'created_at': (datetime.utcnow() - timedelta(days=random.randint(60, 180))).isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'optimization_pattern': scenario["pattern"],
                    'avg_cpu_target': scenario["avg_cpu"]
                }
                resources.append(resource)

                # Generate cost entries with the target pattern
                self._generate_cost_pattern(resource, cost_entries, scenario)
                resource_id += 1

        # Save to files
        resources_file = self.data_dir / "balanced_resources.json"
        cost_entries_file = self.data_dir / "balanced_cost_entries.json"

        with open(resources_file, 'w') as f:
            json.dump(resources, f, indent=2)

        with open(cost_entries_file, 'w') as f:
            json.dump(cost_entries, f, indent=2)

        print(f"   ✅ Generated {len(resources)} resources with optimization patterns")
        print(f"   ✅ Generated {len(cost_entries)} cost entries")
        print(f"   📁 Data saved to {self.data_dir}")

        return resources, cost_entries

    def _generate_cost_pattern(self, resource, cost_entries, scenario):
        """Generate cost entries following specific optimization patterns."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        current_date = start_date
        
        base_cost = scenario["cost_multiplier"] * random.uniform(20, 100)
        pattern = scenario["pattern"]
        avg_cpu = scenario["avg_cpu"]
        
        while current_date <= end_date:
            # Apply pattern-specific cost variation
            if pattern == "low_utilization":
                # Low but variable utilization
                daily_variation = random.uniform(0.1, 0.3)  # 10-30% of capacity
                cost = base_cost * daily_variation
            elif pattern == "high_utilization":
                # Consistently high utilization
                daily_variation = random.uniform(0.8, 1.2)  # 80-120% of capacity
                cost = base_cost * daily_variation
            elif pattern == "consistent_usage":
                # Very consistent usage (good for reserved instances)
                daily_variation = random.uniform(0.9, 1.1)  # 90-110% of capacity
                cost = base_cost * daily_variation
            elif pattern == "spot_candidate":
                # Moderate utilization with some peaks
                daily_variation = random.uniform(0.4, 0.8)  # 40-80% of capacity
                cost = base_cost * daily_variation
            elif pattern == "storage_waste":
                # Low storage utilization
                daily_variation = random.uniform(0.05, 0.2)  # 5-20% of capacity
                cost = base_cost * daily_variation
            elif pattern == "unused":
                # Very low utilization
                daily_variation = random.uniform(0.01, 0.1)  # 1-10% of capacity
                cost = base_cost * daily_variation
            else:
                daily_variation = random.uniform(0.5, 1.5)
                cost = base_cost * daily_variation
            
            # Weekend reduction
            if current_date.weekday() >= 5:
                cost *= 0.7
            
            cost_entry = {
                'resource_id': resource['resource_id'],
                'date': current_date.isoformat(),
                'cost': round(cost, 2),
                'currency': 'USD',
                'usage_quantity': round(random.uniform(10, 100), 2),
                'usage_unit': 'Hours',
                'service': resource['resource_type'],
                'cost_category': 'Storage' if resource['resource_type'] == 'storage' else 'Compute'
            }
            cost_entries.append(cost_entry)
            current_date += timedelta(days=1)

    async def create_tables(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def load_json_file(self, filename: str) -> list:
        """Load data from JSON file."""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r') as f:
            return json.load(f)

    def convert_provider_enum(self, provider_str: str) -> str:
        """Convert provider enum string to database format."""
        # Convert "CloudProvider.AWS" to "aws"
        if "AWS" in provider_str:
            return "aws"
        elif "GCP" in provider_str:
            return "gcp"
        elif "AZURE" in provider_str:
            return "azure"
        else:
            return provider_str.lower()

    def convert_resource_type_enum(self, resource_type_str: str) -> str:
        """Convert resource type enum string to database format."""
        # Map specific resource types to enum values
        resource_type_mapping = {
            'ec2': 'compute',
            'lambda': 'serverless', 
            'rds': 'database',
            'ebs': 'storage',
            's3': 'storage',
            'storage': 'storage',
            'compute': 'compute',
            'database': 'database',
            'serverless': 'serverless',
            'network': 'network',
            'container': 'container'
        }
        
        # Convert "ResourceType.COMPUTE_INSTANCE" to "compute_instance"
        if "." in resource_type_str:
            return resource_type_str.split(".")[1].lower()
        else:
            return resource_type_mapping.get(resource_type_str.lower(), 'other')

    def parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string from JSON."""
        try:
            # Try different datetime formats
            for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            # If no format works, return current time
            return datetime.utcnow()
        except Exception:
            return datetime.utcnow()

    async def load_resources(self, resources_data: list) -> list:
        """Load resources into database."""
        resources = []

        for resource_data in resources_data:
            resource = CloudResource(
                provider=self.convert_provider_enum(resource_data["provider"]),
                resource_id=resource_data["resource_id"],  # This is the string identifier
                resource_type=self.convert_resource_type_enum(resource_data["resource_type"]),
                name=resource_data["name"],
                region=resource_data["region"],
                tags=resource_data.get("tags", {}),
                specifications=resource_data.get("specifications", {}),
                created_at=self.parse_datetime(resource_data.get("created_at", "")),
                updated_at=self.parse_datetime(resource_data.get("updated_at", ""))
            )
            # Store the original string resource_id for mapping
            resource._original_resource_id = resource_data["resource_id"]
            resources.append(resource)

        return resources

    async def load_cost_entries(self, cost_entries_data: list) -> list:
        """Load cost entries into database."""
        cost_entries = []

        for cost_data in cost_entries_data:
            cost_entry = CostEntry(
                resource_id=cost_data["resource_id"],
                date=self.parse_datetime(cost_data["date"]).date(),
                cost=cost_data["cost"],
                currency=cost_data.get("currency", "USD"),
                usage_quantity=cost_data.get("usage_quantity", 0),
                usage_unit=cost_data.get("usage_unit", "Hours"),
                service_name=cost_data.get("service", "unknown"),
                cost_category=cost_data.get("cost_category", "Other")
            )
            cost_entries.append(cost_entry)

        return cost_entries

    async def load_balanced_dataset(self):
        """Load the balanced dataset into database."""
        print("🔄 Loading balanced synthetic dataset...")

        # Load data from JSON files
        print("   📖 Loading resources from JSON...")
        resources_data = self.load_json_file("balanced_resources.json")
        print(f"   ✅ Loaded {len(resources_data)} resources")

        print("   📖 Loading cost entries from JSON...")
        cost_entries_data = self.load_json_file("balanced_cost_entries.json")
        print(f"   ✅ Loaded {len(cost_entries_data)} cost entries")

        # Convert to database objects
        print("   🔄 Converting data to database format...")
        resources = await self.load_resources(resources_data)
        # cost_entries will be created directly in load_balanced_dataset

        # Save to database with proper foreign key mapping
        async with self.async_session() as session:
            print("   💾 Saving resources to database...")
            
            # Create a mapping of original string resource_id to database UUID
            resource_mapping = {}
            for resource in resources:
                original_id = resource._original_resource_id
                session.add(resource)
                await session.flush()  # This assigns the UUID primary key
                resource_mapping[original_id] = resource.id  # Map string ID to UUID
            
            await session.commit()
            print(f"   ✅ Saved {len(resources)} resources")

            print("   💾 Saving cost entries to database...")
            for cost_data in cost_entries_data:
                # Create cost entry with correct UUID reference
                original_resource_id = cost_data["resource_id"]
                if original_resource_id in resource_mapping:
                    cost_entry = CostEntry(
                        resource_id=resource_mapping[original_resource_id],  # Use UUID
                        date=self.parse_datetime(cost_data["date"]).date(),
                        cost=cost_data["cost"],
                        currency=cost_data.get("currency", "USD"),
                        usage_quantity=cost_data.get("usage_quantity", 0),
                        usage_unit=cost_data.get("usage_unit", "Hours"),
                        service_name=cost_data.get("service", "unknown"),
                        cost_category=cost_data.get("cost_category", "Other")
                    )
                    session.add(cost_entry)
                else:
                    print(f"   ⚠️  Warning: No mapping found for resource_id {original_resource_id}")

            await session.commit()
            print(f"   ✅ Saved {len(cost_entries_data)} cost entries")

        print("🎉 Balanced dataset loaded successfully!")

    async def verify_data(self):
        """Verify that data was loaded correctly."""
        print("\n🔍 Verifying loaded data...")

        async with self.async_session() as session:
            # Count resources
            from sqlalchemy import func, select
            resource_count = await session.execute(
                select(func.count()).select_from(CloudResource)
            )
            total_resources = resource_count.scalar()

            # Count cost entries
            cost_count = await session.execute(
                select(func.count()).select_from(CostEntry)
            )
            total_cost_entries = cost_count.scalar()

            # Get providers
            providers = await session.execute(
                select(CloudResource.provider).distinct()
            )
            provider_list = [p[0] for p in providers.all()]

            # Get resource types
            resource_types = await session.execute(
                select(CloudResource.resource_type).distinct()
            )
            resource_type_list = [rt[0] for rt in resource_types.all()]

            print("📊 Database Summary:")
            print(f"   Resources: {total_resources}")
            print(f"   Cost Entries: {total_cost_entries}")
            print(f"   Providers: {', '.join(provider_list)}")
            print(f"   Resource Types: {', '.join(resource_type_list[:5])}{'...' if len(resource_type_list) > 5 else ''}")

            # Calculate total cost
            total_cost_result = await session.execute(
                select(func.sum(CostEntry.cost))
            )
            total_cost = total_cost_result.scalar() or 0
            print(f"   Total Cost: ${total_cost:.2f}")
async def main():
    """Main function to generate and load synthetic data."""
    loader = SyntheticDataLoader()

    try:
        # Generate synthetic data
        loader.generate_synthetic_data()

        # Create tables if they don't exist
        await loader.create_tables()

        # Load balanced dataset
        await loader.load_balanced_dataset()

        # Verify the data
        await loader.verify_data()

        print("\n🎯 Ready to test ML pipeline!")
        print("   Run: curl -X POST http://localhost:8000/api/v1/ml/run-pipeline")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
