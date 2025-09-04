"""
Test Utilities for Synthetic Data

This module provides utilities for loading and using synthetic data in tests,
including fixtures and helper functions for different testing scenarios.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from synthetic_data.generator import (
    MultiCloudDataGenerator,
    SyntheticResource,
    SyntheticCostEntry,
    SyntheticUsagePattern,
    CloudProvider,
    ResourceType
)


class SyntheticDataLoader:
    """Utility class for loading synthetic data from JSON files"""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            # Default to the synthetic_data directory
            self.data_dir = Path(__file__).parent
        else:
            self.data_dir = data_dir

    def load_json(self, filename: str) -> Any:
        """Load data from a JSON file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Synthetic data file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_resources(self, filename: str) -> List[SyntheticResource]:
        """Load resources from JSON file"""
        data = self.load_json(filename)
        resources = []

        for item in data:
            # Convert string dates back to datetime
            created_at = datetime.fromisoformat(item['created_at']) if 'created_at' in item else None
            updated_at = datetime.fromisoformat(item['updated_at']) if 'updated_at' in item else None

            # Handle enum values that might be stored as full enum strings
            provider_str = item['provider']
            if provider_str.startswith('CloudProvider.'):
                provider_str = provider_str.split('.')[-1].lower()
            provider = CloudProvider(provider_str)

            resource_type_str = item['resource_type']
            if resource_type_str.startswith('ResourceType.'):
                # Extract the enum name and map to the correct value
                enum_name = resource_type_str.split('.')[-1]
                if enum_name == 'COMPUTE_INSTANCE':
                    resource_type_str = 'compute'
                elif enum_name == 'DATABASE':
                    resource_type_str = 'database'
                elif enum_name == 'STORAGE':
                    resource_type_str = 'storage'
                elif enum_name == 'NETWORK':
                    resource_type_str = 'network'
                elif enum_name == 'CONTAINER':
                    resource_type_str = 'container'
                elif enum_name == 'SERVERLESS':
                    resource_type_str = 'serverless'
                else:
                    resource_type_str = enum_name.lower()
            resource_type = ResourceType(resource_type_str)

            resource = SyntheticResource(
                id=item['id'],
                provider=provider,
                resource_id=item['resource_id'],
                resource_type=resource_type,
                name=item['name'],
                region=item['region'],
                tags=item.get('tags', {}),
                specifications=item.get('specifications', {}),
                created_at=created_at,
                updated_at=updated_at
            )
            resources.append(resource)

        return resources

    def load_cost_entries(self, filename: str) -> List[SyntheticCostEntry]:
        """Load cost entries from JSON file"""
        data = self.load_json(filename)
        cost_entries = []

        for item in data:
            # Handle enum values that might be stored as full enum strings
            provider_str = item['provider']
            if provider_str.startswith('CloudProvider.'):
                provider_str = provider_str.split('.')[-1].lower()
            provider = CloudProvider(provider_str)

            cost_entry = SyntheticCostEntry(
                id=item['id'],
                resource_id=item['resource_id'],
                provider=provider,
                service=item['service'],
                cost=item['cost'],
                currency=item.get('currency', 'USD'),
                date=datetime.fromisoformat(item['date']),
                region=item['region'],
                tags=item.get('tags', {})
            )
            cost_entries.append(cost_entry)

        return cost_entries

    def load_usage_patterns(self, filename: str) -> List[SyntheticUsagePattern]:
        """Load usage patterns from JSON file"""
        data = self.load_json(filename)
        usage_patterns = []

        for item in data:
            usage_pattern = SyntheticUsagePattern(
                resource_id=item['resource_id'],
                date=datetime.fromisoformat(item['date']),
                cpu_utilization=item['cpu_utilization'],
                memory_utilization=item['memory_utilization'],
                network_in=item['network_in'],
                network_out=item['network_out'],
                storage_used=item['storage_used'],
                requests_per_minute=item.get('requests_per_minute')
            )
            usage_patterns.append(usage_pattern)

        return usage_patterns

    def load_complete_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Load a complete scenario with all components"""
        base_name = f"{scenario_name}_complete.json"
        return self.load_json(base_name)


# Pytest fixtures for different test scenarios
@pytest.fixture
def synthetic_data_loader():
    """Fixture to provide a synthetic data loader"""
    return SyntheticDataLoader()


@pytest.fixture
def minimal_resources(synthetic_data_loader):
    """Fixture for minimal test resources"""
    return synthetic_data_loader.load_resources("test_minimal_resources.json")


@pytest.fixture
def small_dataset(synthetic_data_loader):
    """Fixture for small test dataset"""
    return synthetic_data_loader.load_complete_scenario("test_small")


@pytest.fixture
def medium_dataset(synthetic_data_loader):
    """Fixture for medium test dataset"""
    return synthetic_data_loader.load_complete_scenario("test_medium")


@pytest.fixture
def balanced_scenario(synthetic_data_loader):
    """Fixture for balanced multi-cloud scenario"""
    return synthetic_data_loader.load_complete_scenario("balanced")


@pytest.fixture
def aws_resources_only(synthetic_data_loader):
    """Fixture for AWS-only resources"""
    return synthetic_data_loader.load_resources("aws_resources.json")


@pytest.fixture
def multi_cloud_resources(synthetic_data_loader):
    """Fixture for resources across all cloud providers"""
    aws_resources = synthetic_data_loader.load_resources("aws_resources.json")
    gcp_resources = synthetic_data_loader.load_resources("gcp_resources.json")
    azure_resources = synthetic_data_loader.load_resources("azure_resources.json")

    return aws_resources + gcp_resources + azure_resources


@pytest.fixture
def cost_anomaly_scenario(synthetic_data_loader):
    """Fixture for cost anomaly test scenario"""
    return synthetic_data_loader.load_complete_scenario("cost_anomaly")


# Helper functions for test data manipulation
def filter_resources_by_provider(resources: List[SyntheticResource],
                               provider: CloudProvider) -> List[SyntheticResource]:
    """Filter resources by cloud provider"""
    return [r for r in resources if r.provider == provider]


def filter_resources_by_type(resources: List[SyntheticResource],
                           resource_type: ResourceType) -> List[SyntheticResource]:
    """Filter resources by resource type"""
    return [r for r in resources if r.resource_type == resource_type]


def get_cost_entries_for_resource(cost_entries: List[SyntheticCostEntry],
                                resource_id: str) -> List[SyntheticCostEntry]:
    """Get all cost entries for a specific resource"""
    return [ce for ce in cost_entries if ce.resource_id == resource_id]


def calculate_total_cost(cost_entries: List[SyntheticCostEntry]) -> float:
    """Calculate total cost from cost entries"""
    return sum(ce.cost for ce in cost_entries)


def get_usage_patterns_for_resource(usage_patterns: List[SyntheticUsagePattern],
                                  resource_id: str) -> List[SyntheticUsagePattern]:
    """Get all usage patterns for a specific resource"""
    return [up for up in usage_patterns if up.resource_id == resource_id]


def generate_test_resource(provider: CloudProvider = CloudProvider.AWS,
                          resource_type: ResourceType = ResourceType.COMPUTE_INSTANCE,
                          region: str = "us-east-1") -> SyntheticResource:
    """Generate a single test resource for unit tests"""
    generator = MultiCloudDataGenerator(seed=12345)
    return generator.generate_single_resource(provider, resource_type, region)


def generate_test_cost_entries(resource: SyntheticResource, days: int = 7) -> List[SyntheticCostEntry]:
    """Generate test cost entries for a resource"""
    generator = MultiCloudDataGenerator(seed=12345)
    return generator.generate_cost_entries([resource], days=days)


# Test data validation helpers
def validate_resource_data(resource: SyntheticResource) -> bool:
    """Validate that a resource has all required fields"""
    required_fields = ['id', 'provider', 'resource_id', 'resource_type', 'name', 'region']
    return all(hasattr(resource, field) for field in required_fields)


def validate_cost_entry_data(cost_entry: SyntheticCostEntry) -> bool:
    """Validate that a cost entry has all required fields"""
    required_fields = ['id', 'resource_id', 'provider', 'service', 'cost', 'date', 'region']
    return all(hasattr(cost_entry, field) for field in required_fields)


def validate_usage_pattern_data(usage_pattern: SyntheticUsagePattern) -> bool:
    """Validate that a usage pattern has all required fields"""
    required_fields = ['resource_id', 'date', 'cpu_utilization', 'memory_utilization',
                      'network_in', 'network_out', 'storage_used']
    return all(hasattr(usage_pattern, field) for field in required_fields)


# Performance testing helpers
def generate_large_dataset(size: str = "large") -> Dict[str, Any]:
    """Generate a large dataset for performance testing"""
    if size == "large":
        resource_count = 500
        days = 90
    elif size == "xlarge":
        resource_count = 1000
        days = 180
    else:
        resource_count = 100
        days = 30

    generator = MultiCloudDataGenerator(seed=42)
    resources = generator.generate_resources(count=resource_count)
    cost_entries = generator.generate_cost_entries(resources, days=days)
    usage_patterns = generator.generate_usage_patterns(resources, days=min(days, 30))

    return {
        "resources": resources,
        "cost_entries": cost_entries,
        "usage_patterns": usage_patterns,
        "summary": {
            "total_resources": len(resources),
            "total_cost_entries": len(cost_entries),
            "total_usage_patterns": len(usage_patterns),
            "total_cost": calculate_total_cost(cost_entries)
        }
    }


# Example usage and test data
def create_example_test_data():
    """Create example test data for documentation"""
    generator = MultiCloudDataGenerator(seed=42)

    # Generate a small multi-cloud scenario
    resources = generator.generate_resources(count=10)
    cost_entries = generator.generate_cost_entries(resources, days=7)
    usage_patterns = generator.generate_usage_patterns(resources, days=3)

    return {
        "resources": [r.__dict__ for r in resources],
        "cost_entries": [ce.__dict__ for ce in cost_entries],
        "usage_patterns": [up.__dict__ for up in usage_patterns]
    }


if __name__ == "__main__":
    # Generate example data when run directly
    print("Generating example synthetic test data...")
    example_data = create_example_test_data()

    print(f"Generated {len(example_data['resources'])} resources")
    print(f"Generated {len(example_data['cost_entries'])} cost entries")
    print(f"Generated {len(example_data['usage_patterns'])} usage patterns")

    # Save example data
    output_file = Path(__file__).parent / "example_test_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(example_data, f, indent=2, default=str)

    print(f"Example data saved to: {output_file}")
