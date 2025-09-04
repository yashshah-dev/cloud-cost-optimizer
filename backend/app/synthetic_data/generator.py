"""
Synthetic Data Generators for Multi-Cloud Testing

This module provides realistic synthetic data generation for testing the Cloud Cost Optimizer
across multiple cloud providers (AWS, GCP, Azure) with various usage patterns and scenarios.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class ResourceType(Enum):
    COMPUTE_INSTANCE = "compute"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"


@dataclass
class SyntheticResource:
    """Represents a synthetic cloud resource"""
    id: str
    provider: CloudProvider
    resource_id: str
    resource_type: ResourceType
    name: str
    region: str
    tags: Dict[str, str]
    specifications: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class SyntheticCostEntry:
    """Represents a synthetic cost entry"""
    id: str
    resource_id: str
    provider: CloudProvider
    service: str
    cost: float
    currency: str
    date: datetime
    region: str
    tags: Dict[str, str]


@dataclass
class SyntheticUsagePattern:
    """Represents usage patterns for a resource"""
    resource_id: str
    date: datetime
    cpu_utilization: float
    memory_utilization: float
    network_in: float
    network_out: float
    storage_used: float
    requests_per_minute: Optional[float] = None


class MultiCloudDataGenerator:
    """Main generator for synthetic multi-cloud data"""

    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional random seed for reproducible results"""
        if seed:
            random.seed(seed)

        # AWS regions
        self.aws_regions = [
            "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1",
            "ca-central-1", "sa-east-1", "eu-central-1", "ap-northeast-1"
        ]

        # GCP regions
        self.gcp_regions = [
            "us-central1", "us-east1", "us-west1", "europe-west1",
            "asia-southeast1", "australia-southeast1", "europe-north1"
        ]

        # Azure regions
        self.azure_regions = [
            "East US", "West US 2", "North Europe", "Southeast Asia",
            "Canada Central", "Brazil South", "Germany West Central"
        ]

        # Resource name templates
        self.resource_templates = {
            CloudProvider.AWS: {
                ResourceType.COMPUTE_INSTANCE: ["web-server-{num}", "app-server-{num}", "worker-{num}"],
                ResourceType.DATABASE: ["postgres-db-{num}", "mysql-cluster-{num}", "redis-cache-{num}"],
                ResourceType.STORAGE: ["app-bucket-{num}", "logs-bucket-{num}", "backup-bucket-{num}"],
                ResourceType.SERVERLESS: ["lambda-{num}", "api-gateway-{num}"]
            },
            CloudProvider.GCP: {
                ResourceType.COMPUTE_INSTANCE: ["gce-instance-{num}", "gke-node-{num}", "cloud-run-{num}"],
                ResourceType.DATABASE: ["cloud-sql-{num}", "bigtable-{num}", "memorystore-{num}"],
                ResourceType.STORAGE: ["gcs-bucket-{num}", "filestore-{num}"],
                ResourceType.SERVERLESS: ["cloud-function-{num}", "cloud-run-{num}"]
            },
            CloudProvider.AZURE: {
                ResourceType.COMPUTE_INSTANCE: ["vm-{num}", "aks-node-{num}", "container-app-{num}"],
                ResourceType.DATABASE: ["sql-server-{num}", "cosmos-db-{num}", "cache-{num}"],
                ResourceType.STORAGE: ["storage-account-{num}", "file-share-{num}"],
                ResourceType.SERVERLESS: ["function-app-{num}", "logic-app-{num}"]
            }
        }

    def get_regions_for_provider(self, provider: CloudProvider) -> List[str]:
        """Get available regions for a cloud provider"""
        if provider == CloudProvider.AWS:
            return self.aws_regions
        elif provider == CloudProvider.GCP:
            return self.gcp_regions
        elif provider == CloudProvider.AZURE:
            return self.azure_regions
        return []

    def generate_resource_name(self, provider: CloudProvider, resource_type: ResourceType) -> str:
        """Generate a realistic resource name"""
        templates = self.resource_templates.get(provider, {}).get(resource_type, ["resource-{num}"])
        template = random.choice(templates)
        return template.format(num=random.randint(1, 999))

    def generate_resource_id(self, provider: CloudProvider, resource_type: ResourceType) -> str:
        """Generate a provider-specific resource ID"""
        if provider == CloudProvider.AWS:
            if resource_type == ResourceType.COMPUTE_INSTANCE:
                return f"i-{uuid.uuid4().hex[:17]}"
            elif resource_type == ResourceType.DATABASE:
                return f"db-{uuid.uuid4().hex[:12]}"
            elif resource_type == ResourceType.STORAGE:
                return f"my-bucket-{random.randint(100, 999)}"
        elif provider == CloudProvider.GCP:
            if resource_type == ResourceType.COMPUTE_INSTANCE:
                return f"projects/my-project/zones/us-central1-a/instances/{uuid.uuid4().hex[:8]}"
            elif resource_type == ResourceType.STORAGE:
                return f"my-project.appspot.com/{uuid.uuid4().hex[:16]}"
        elif provider == CloudProvider.AZURE:
            if resource_type == ResourceType.COMPUTE_INSTANCE:
                return f"/subscriptions/{uuid.uuid4()}/resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/vm{random.randint(1, 999)}"

        return str(uuid.uuid4())

    def generate_tags(self, provider: CloudProvider) -> Dict[str, str]:
        """Generate realistic tags for a resource"""
        base_tags = {
            "Environment": random.choice(["production", "staging", "development", "test"]),
            "Team": random.choice(["backend", "frontend", "data", "infra", "security"]),
            "Project": random.choice(["web-app", "api", "analytics", "ml-pipeline", "monitoring"])
        }

        # Provider-specific tags
        if provider == CloudProvider.AWS:
            base_tags["Owner"] = random.choice(["john.doe", "jane.smith", "admin"])
        elif provider == CloudProvider.GCP:
            base_tags["created-by"] = random.choice(["terraform", "gcloud", "console"])
        elif provider == CloudProvider.AZURE:
            base_tags["createdBy"] = random.choice(["terraform", "portal", "cli"])

        return base_tags

    def generate_specifications(self, resource_type: ResourceType) -> Dict[str, Any]:
        """Generate realistic specifications for a resource type"""
        if resource_type == ResourceType.COMPUTE_INSTANCE:
            return {
                "instance_type": random.choice(["t3.medium", "t3.large", "m5.large", "c5.xlarge"]),
                "vcpus": random.choice([2, 4, 8, 16]),
                "memory_gb": random.choice([4, 8, 16, 32, 64]),
                "storage_gb": random.choice([20, 50, 100, 200])
            }
        elif resource_type == ResourceType.DATABASE:
            return {
                "engine": random.choice(["postgres", "mysql", "mongodb"]),
                "instance_type": random.choice(["db.t3.medium", "db.t3.large", "db.r5.large"]),
                "storage_gb": random.choice([20, 100, 500, 1000]),
                "multi_az": random.choice([True, False])
            }
        elif resource_type == ResourceType.STORAGE:
            return {
                "storage_class": random.choice(["STANDARD", "STANDARD_IA", "GLACIER"]),
                "versioning": random.choice([True, False]),
                "encryption": True
            }
        elif resource_type == ResourceType.SERVERLESS:
            return {
                "runtime": random.choice(["python3.9", "node14", "java11"]),
                "memory_mb": random.choice([128, 256, 512, 1024]),
                "timeout_seconds": random.choice([30, 60, 300, 900])
            }

        return {}

    def generate_single_resource(self, provider: CloudProvider, resource_type: ResourceType,
                               region: Optional[str] = None) -> SyntheticResource:
        """Generate a single synthetic resource"""
        if not region:
            regions = self.get_regions_for_provider(provider)
            region = random.choice(regions) if regions else "us-east-1"

        created_at = datetime.now() - timedelta(days=random.randint(1, 365))
        updated_at = created_at + timedelta(hours=random.randint(1, 24*30))

        return SyntheticResource(
            id=str(uuid.uuid4()),
            provider=provider,
            resource_id=self.generate_resource_id(provider, resource_type),
            resource_type=resource_type,
            name=self.generate_resource_name(provider, resource_type),
            region=region,
            tags=self.generate_tags(provider),
            specifications=self.generate_specifications(resource_type),
            created_at=created_at,
            updated_at=updated_at
        )

    def generate_resources(self, count: int = 50, providers: Optional[List[CloudProvider]] = None) -> List[SyntheticResource]:
        """Generate multiple synthetic resources across providers"""
        if not providers:
            providers = [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]

        resources = []
        for _ in range(count):
            provider = random.choice(providers)
            resource_type = random.choice(list(ResourceType))
            resource = self.generate_single_resource(provider, resource_type)
            resources.append(resource)

        return resources

    def generate_cost_entries(self, resources: List[SyntheticResource], days: int = 30) -> List[SyntheticCostEntry]:
        """Generate synthetic cost entries for resources over a time period"""
        cost_entries = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for resource in resources:
            current_date = start_date
            while current_date <= end_date:
                # Generate daily cost with some variation
                base_cost = self._calculate_base_cost(resource)
                daily_variation = random.uniform(0.8, 1.2)  # ±20% variation
                seasonal_factor = self._get_seasonal_factor(current_date)
                cost = base_cost * daily_variation * seasonal_factor

                cost_entry = SyntheticCostEntry(
                    id=str(uuid.uuid4()),
                    resource_id=resource.id,
                    provider=resource.provider,
                    service=resource.resource_type.value,
                    cost=round(cost, 2),
                    currency="USD",
                    date=current_date,
                    region=resource.region,
                    tags=resource.tags
                )
                cost_entries.append(cost_entry)
                current_date += timedelta(days=1)

        return cost_entries

    def _calculate_base_cost(self, resource: SyntheticResource) -> float:
        """Calculate base daily cost for a resource"""
        base_costs = {
            ResourceType.COMPUTE_INSTANCE: 15.0,
            ResourceType.DATABASE: 25.0,
            ResourceType.STORAGE: 2.0,
            ResourceType.NETWORK: 5.0,
            ResourceType.CONTAINER: 8.0,
            ResourceType.SERVERLESS: 1.0
        }

        base_cost = base_costs.get(resource.resource_type, 10.0)

        # Adjust based on specifications
        if resource.resource_type == ResourceType.COMPUTE_INSTANCE:
            vcpus = resource.specifications.get("vcpus", 2)
            base_cost *= (vcpus / 2.0)
        elif resource.resource_type == ResourceType.DATABASE:
            storage = resource.specifications.get("storage_gb", 100)
            base_cost *= (storage / 100.0)

        return base_cost

    def _get_seasonal_factor(self, date: datetime) -> float:
        """Get seasonal cost factor (weekends, holidays, etc.)"""
        # Weekend factor
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return random.uniform(0.9, 1.1)

        # Business hours factor (higher during business hours)
        hour = date.hour
        if 9 <= hour <= 17:
            return random.uniform(1.0, 1.2)
        else:
            return random.uniform(0.8, 1.0)

    def generate_usage_patterns(self, resources: List[SyntheticResource], days: int = 7) -> List[SyntheticUsagePattern]:
        """Generate synthetic usage patterns for resources"""
        usage_patterns = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for resource in resources:
            current_date = start_date
            while current_date <= end_date:
                # Generate hourly usage patterns
                for hour in range(24):
                    usage_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)

                    # Base utilization varies by resource type
                    if resource.resource_type == ResourceType.COMPUTE_INSTANCE:
                        cpu_base = random.uniform(20, 80)
                        memory_base = random.uniform(30, 90)
                        network_base = random.uniform(10, 50)
                        storage_base = random.uniform(40, 80)
                    elif resource.resource_type == ResourceType.DATABASE:
                        cpu_base = random.uniform(15, 60)
                        memory_base = random.uniform(25, 75)
                        network_base = random.uniform(5, 30)
                        storage_base = random.uniform(50, 90)
                    else:
                        cpu_base = random.uniform(10, 50)
                        memory_base = random.uniform(20, 60)
                        network_base = random.uniform(5, 25)
                        storage_base = random.uniform(30, 70)

                    # Add time-of-day variation
                    time_factor = self._get_time_factor(hour)
                    cpu_util = min(100, cpu_base * time_factor + random.uniform(-10, 10))
                    memory_util = min(100, memory_base * time_factor + random.uniform(-10, 10))
                    network_in = network_base * time_factor + random.uniform(-5, 5)
                    network_out = network_base * time_factor + random.uniform(-5, 5)
                    storage_used = storage_base + random.uniform(-5, 5)

                    usage_pattern = SyntheticUsagePattern(
                        resource_id=resource.id,
                        date=usage_time,
                        cpu_utilization=max(0, cpu_util),
                        memory_utilization=max(0, memory_util),
                        network_in=max(0, network_in),
                        network_out=max(0, network_out),
                        storage_used=max(0, storage_used)
                    )
                    usage_patterns.append(usage_pattern)

                current_date += timedelta(days=1)

        return usage_patterns

    def _get_time_factor(self, hour: int) -> float:
        """Get time-of-day utilization factor"""
        if 9 <= hour <= 17:  # Business hours
            return random.uniform(1.2, 1.5)
        elif 18 <= hour <= 22:  # Evening
            return random.uniform(0.8, 1.1)
        else:  # Night/early morning
            return random.uniform(0.3, 0.7)

    def generate_multi_cloud_scenario(self, scenario_type: str = "balanced") -> Dict[str, Any]:
        """Generate a complete multi-cloud scenario with resources, costs, and usage"""
        if scenario_type == "balanced":
            # Balanced distribution across providers
            resources = self.generate_resources(count=30)
        elif scenario_type == "aws_heavy":
            # Mostly AWS resources
            aws_resources = [r for r in self.generate_resources(count=40) if r.provider == CloudProvider.AWS]
            other_resources = [r for r in self.generate_resources(count=10) if r.provider != CloudProvider.AWS]
            resources = aws_resources + other_resources
        elif scenario_type == "cost_anomaly":
            # Include some high-cost resources
            resources = self.generate_resources(count=25)
            # Add expensive resources
            expensive_compute = self.generate_single_resource(CloudProvider.AWS, ResourceType.COMPUTE_INSTANCE)
            expensive_compute.specifications = {"instance_type": "p3.8xlarge", "vcpus": 32, "memory_gb": 244}
            resources.append(expensive_compute)
        else:
            resources = self.generate_resources(count=30)

        cost_entries = self.generate_cost_entries(resources, days=30)
        usage_patterns = self.generate_usage_patterns(resources, days=7)

        return {
            "scenario_type": scenario_type,
            "resources": resources,
            "cost_entries": cost_entries,
            "usage_patterns": usage_patterns,
            "summary": {
                "total_resources": len(resources),
                "total_cost": sum(ce.cost for ce in cost_entries),
                "providers": list(set(r.provider.value for r in resources)),
                "resource_types": list(set(r.resource_type.value for r in resources))
            }
        }


# Convenience functions for quick data generation
def generate_aws_resources(count: int = 20) -> List[SyntheticResource]:
    """Generate AWS-specific resources"""
    generator = MultiCloudDataGenerator()
    return [r for r in generator.generate_resources(count * 2) if r.provider == CloudProvider.AWS][:count]


def generate_gcp_resources(count: int = 20) -> List[SyntheticResource]:
    """Generate GCP-specific resources"""
    generator = MultiCloudDataGenerator()
    return [r for r in generator.generate_resources(count * 2) if r.provider == CloudProvider.GCP][:count]


def generate_azure_resources(count: int = 20) -> List[SyntheticResource]:
    """Generate Azure-specific resources"""
    generator = MultiCloudDataGenerator()
    return [r for r in generator.generate_resources(count * 2) if r.provider == CloudProvider.AZURE][:count]


def generate_multi_cloud_dataset() -> Dict[str, Any]:
    """Generate a complete multi-cloud dataset for testing"""
    generator = MultiCloudDataGenerator(seed=42)  # Reproducible results
    return generator.generate_multi_cloud_scenario("balanced")


if __name__ == "__main__":
    # Example usage
    generator = MultiCloudDataGenerator(seed=42)

    # Generate a balanced multi-cloud scenario
    scenario = generator.generate_multi_cloud_scenario("balanced")

    print(f"Generated scenario: {scenario['scenario_type']}")
    print(f"Total resources: {scenario['summary']['total_resources']}")
    print(f"Total cost: ${scenario['summary']['total_cost']:.2f}")
    print(f"Providers: {', '.join(scenario['summary']['providers'])}")
    print(f"Resource types: {', '.join(scenario['summary']['resource_types'])}")

    # Show sample resource
    if scenario['resources']:
        sample = scenario['resources'][0]
        print(f"\nSample resource: {sample.name}")
        print(f"Provider: {sample.provider.value}")
        print(f"Type: {sample.resource_type.value}")
        print(f"Region: {sample.region}")
        print(f"Tags: {sample.tags}")
