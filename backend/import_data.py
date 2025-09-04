#!/usr/bin/env python3
"""
Import synthetic data into the database
"""

import asyncio
import json
import sys
from datetime import datetime
from uuid import uuid4

from app.database import async_session_maker
from app.models import CloudResource, CostEntry, OptimizationRecommendation

async def import_synthetic_data():
    """Import generated synthetic data into the database"""
    print("🚀 Starting synthetic data import...")
    
    # Load JSON files
    print("📂 Loading data files...")
    with open('synthetic_data/resources.json', 'r') as f:
        resources_data = json.load(f)
    
    with open('synthetic_data/cost_entries.json', 'r') as f:
        cost_entries_data = json.load(f)
    
    print(f"📊 Loaded {len(resources_data)} resources and {len(cost_entries_data)} cost entries")
    
    async with async_session_maker() as session:
        # Import resources
        print("💾 Importing resources...")
        resource_id_map = {}
        
        for resource_data in resources_data:
            # Generate UUID for database
            db_id = str(uuid4())
            resource_id_map[resource_data['id']] = db_id
            
            resource = CloudResource(
                id=db_id,
                provider=resource_data['provider'],
                resource_id=resource_data['id'],
                resource_type=resource_data['resource_type'],
                name=resource_data['name'],
                region=resource_data['region'],
                tags=resource_data.get('tags', {}),
                specifications={"instance_type": resource_data.get('instance_type', 'unknown')},
                created_at=datetime.fromisoformat(resource_data['created_at'].replace('Z', '+00:00'))
            )
            session.add(resource)
        
        await session.commit()
        print(f"✅ Imported {len(resources_data)} resources")
        
        # Import cost entries in batches
        print("💰 Importing cost entries...")
        batch_size = 1000
        
        for i in range(0, len(cost_entries_data), batch_size):
            batch = cost_entries_data[i:i + batch_size]
            
            for cost_data in batch:
                # Skip if resource doesn't exist
                if cost_data['resource_id'] not in resource_id_map:
                    continue
                    
                cost_entry = CostEntry(
                    id=str(uuid4()),
                    resource_id=resource_id_map[cost_data['resource_id']],
                    date=datetime.fromisoformat(cost_data['date']),
                    cost=cost_data['cost'],
                    currency='USD',
                    usage_quantity=cost_data.get('usage_quantity', 0),
                    usage_unit=cost_data.get('usage_unit', 'hours'),
                    service_name=cost_data['service_name'],
                    cost_category='compute'
                )
                session.add(cost_entry)
            
            await session.commit()
            print(f"📈 Imported batch {i//batch_size + 1}/{(len(cost_entries_data) + batch_size - 1)//batch_size}")
        
        print(f"✅ Imported {len(cost_entries_data)} cost entries")
        
        # Create some sample optimization recommendations
        print("🎯 Creating sample optimization recommendations...")
        
        # Get first 3 resources for recommendations
        sample_resources = list(resource_id_map.values())[:3]
        
        optimizations = [
            OptimizationRecommendation(
                id="fbb20122-f92a-4cbb-869a-bab3bfd9bd8e",
                resource_id=sample_resources[0],
                type="rightsizing",
                title="Rightsize EC2 Instance",
                description="Based on CPU utilization analysis, this instance can be downsized without impacting performance.",
                potential_savings=45.20,
                confidence_score=0.85,
                risk_level="low",
                status="pending",
                recommendation_data={
                    "current_instance_type": "m5.large",
                    "recommended_instance_type": "m5.medium",
                    "avg_cpu_utilization": 35.2
                }
            ),
            OptimizationRecommendation(
                id="gcc31233-c43b-5704-cc33-fdf9d933e260",
                resource_id=sample_resources[1],
                type="reserved_instances",
                title="Purchase Reserved Instances",
                description="This instance runs consistently. Reserved Instance would provide cost savings.",
                potential_savings=892.50,
                confidence_score=0.92,
                risk_level="low",
                status="pending",
                recommendation_data={
                    "current_pricing": "on-demand",
                    "recommended_pricing": "reserved-1year",
                    "annual_savings": 892.50
                }
            ),
            OptimizationRecommendation(
                id="hdd42344-d54c-6815-dd44-gef0e044f371",
                resource_id=sample_resources[2],
                type="storage_optimization", 
                title="Optimize Storage",
                description="Storage utilization analysis suggests optimization opportunities.",
                potential_savings=125.30,
                confidence_score=0.78,
                risk_level="medium",
                status="pending",
                recommendation_data={
                    "storage_utilization": "60%",
                    "recommendation": "Enable auto-scaling"
                }
            )
        ]
        
        for opt in optimizations:
            session.add(opt)
        
        await session.commit()
        print(f"✅ Created {len(optimizations)} optimization recommendations")
    
    print("🎉 Synthetic data import completed successfully!")
    print(f"\n📋 Summary:")
    print(f"   • Imported {len(resources_data)} cloud resources")
    print(f"   • Imported {len(cost_entries_data)} cost entries")
    print(f"   • Created {len(optimizations)} optimization recommendations")
    print(f"\n🧪 Test the explain-optimization endpoint with:")
    print(f"   optimization_id: fbb20122-f92a-4cbb-869a-bab3bfd9bd8e")
    print(f"   resource_id: {sample_resources[0]}")

if __name__ == "__main__":
    asyncio.run(import_synthetic_data())
