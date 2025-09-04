#!/usr/bin/env python3
"""
Sample data population script for Cloud Cost Optimizer
Adds sample cloud resources and cost data for testing
"""

import asyncio
import sys
from datetime import datetime, timedelta
import uuid

from app.database import async_session_maker
from app.models import CloudResource, CostEntry, OptimizationRecommendation

async def populate_sample_data():
    """Populate database with sample data"""
    try:
        print("🌱 Populating sample data...")

        async with async_session_maker() as session:
            # Create sample cloud resources
            resources = [
                CloudResource(
                    id=uuid.uuid4(),
                    provider="aws",
                    resource_id="i-1234567890abcdef0",
                    resource_type="compute",  # Changed from 'ec2'
                    name="web-server-01",
                    region="us-east-1",
                    tags={"Environment": "production", "Team": "web"},
                    specifications={"instance_type": "t3.medium", "vcpus": 2, "memory_gb": 4}
                ),
                CloudResource(
                    id=uuid.uuid4(),
                    provider="aws",
                    resource_id="db-1234567890abcdef0",
                    resource_type="database",  # Changed from 'rds'
                    name="postgres-db-01",
                    region="us-east-1",
                    tags={"Environment": "production", "Team": "data"},
                    specifications={"instance_type": "db.t3.medium", "engine": "postgres", "storage_gb": 100}
                ),
                CloudResource(
                    id=uuid.uuid4(),
                    provider="gcp",
                    resource_id="projects/my-project/zones/us-central1-a/instances/gce-instance-1",
                    resource_type="compute",  # Changed from 'compute_engine'
                    name="gcp-web-server",
                    region="us-central1",
                    tags={"environment": "production", "team": "web"},
                    specifications={"machine_type": "n1-standard-2", "vcpus": 2, "memory_gb": 7.5}
                )
            ]

            # Add resources to session
            for resource in resources:
                session.add(resource)
            await session.commit()

            print(f"✅ Created {len(resources)} sample resources")

            # Create sample cost entries for the last 30 days
            cost_entries = []
            base_date = datetime.utcnow() - timedelta(days=30)

            for i in range(30):
                current_date = base_date + timedelta(days=i)

                # EC2 instance costs (~$30/day)
                cost_entries.append(CostEntry(
                    resource_id=resources[0].id,
                    date=current_date,
                    cost=32.50,
                    currency="USD",
                    usage_quantity=24.0,
                    usage_unit="hours",
                    service_name="Amazon Elastic Compute Cloud",
                    cost_category="compute"
                ))

                # RDS instance costs (~$50/day)
                cost_entries.append(CostEntry(
                    resource_id=resources[1].id,
                    date=current_date,
                    cost=52.30,
                    currency="USD",
                    usage_quantity=24.0,
                    usage_unit="hours",
                    service_name="Amazon Relational Database Service",
                    cost_category="database"
                ))

                # GCP Compute Engine costs (~$25/day)
                cost_entries.append(CostEntry(
                    resource_id=resources[2].id,
                    date=current_date,
                    cost=28.75,
                    currency="USD",
                    usage_quantity=24.0,
                    usage_unit="hours",
                    service_name="Compute Engine",
                    cost_category="compute"
                ))

            # Add cost entries to session
            for entry in cost_entries:
                session.add(entry)
            await session.commit()

            print(f"✅ Created {len(cost_entries)} sample cost entries")

            # Create sample optimization recommendations
            recommendations = [
                OptimizationRecommendation(
                    resource_id=resources[0].id,
                    type="rightsizing",
                    title="Downsize EC2 Instance",
                    description="Current t3.medium instance is over-provisioned. Consider t3.small for cost savings.",
                    potential_savings=450.0,
                    confidence_score=0.85,
                    risk_level="low",
                    status="pending",
                    recommendation_data={
                        "current_instance_type": "t3.medium",
                        "recommended_instance_type": "t3.small",
                        "estimated_monthly_savings": 450.0,
                        "cpu_utilization_avg": 0.35,
                        "memory_utilization_avg": 0.42
                    },
                    expires_at=datetime.utcnow() + timedelta(days=30)
                ),
                OptimizationRecommendation(
                    resource_id=resources[1].id,
                    type="reserved_instance",
                    title="Purchase Reserved Instance",
                    description="Consider purchasing a 1-year reserved instance for significant cost savings.",
                    potential_savings=1200.0,
                    confidence_score=0.92,
                    risk_level="medium",
                    status="pending",
                    recommendation_data={
                        "current_pricing": "on_demand",
                        "recommended_pricing": "reserved_1year",
                        "estimated_monthly_savings": 1200.0,
                        "break_even_months": 8
                    },
                    expires_at=datetime.utcnow() + timedelta(days=60)
                ),
                OptimizationRecommendation(
                    resource_id=resources[2].id,
                    type="spot_instance",
                    title="Use Spot Instances",
                    description="Switch to spot instances for non-critical workloads to reduce costs by up to 70%.",
                    potential_savings=630.0,
                    confidence_score=0.78,
                    risk_level="high",
                    status="pending",
                    recommendation_data={
                        "current_pricing": "on_demand",
                        "recommended_pricing": "spot",
                        "estimated_monthly_savings": 630.0,
                        "spot_price_variability": "medium"
                    },
                    expires_at=datetime.utcnow() + timedelta(days=45)
                )
            ]

            # Add recommendations to session
            for rec in recommendations:
                session.add(rec)
            await session.commit()

            print(f"✅ Created {len(recommendations)} sample optimization recommendations")

        print("🎉 Sample data population completed!")
        return True

    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        return False

async def main():
    """Main function"""
    success = await populate_sample_data()
    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
