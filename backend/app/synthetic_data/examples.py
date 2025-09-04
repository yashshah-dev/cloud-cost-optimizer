#!/usr/bin/env python3
"""
Example Usage of Synthetic Data Generators

This script demonstrates how to use the synthetic data generators
for testing the Cloud Cost Optimizer application.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from synthetic_data.generator import MultiCloudDataGenerator, CloudProvider, ResourceType
from synthetic_data.test_utils import (
    SyntheticDataLoader,
    filter_resources_by_provider,
    calculate_total_cost,
    generate_test_resource
)


def example_basic_generation():
    """Example of basic synthetic data generation"""
    print("🔄 Basic Synthetic Data Generation Example")
    print("=" * 50)

    # Create generator with fixed seed for reproducible results
    generator = MultiCloudDataGenerator(seed=42)

    # Generate a balanced multi-cloud scenario
    scenario = generator.generate_multi_cloud_scenario("balanced")

    print(f"Scenario Type: {scenario['scenario_type']}")
    print(f"Total Resources: {scenario['summary']['total_resources']}")
    print(f"Total Cost: ${scenario['summary']['total_cost']:.2f}")
    print(f"Providers: {', '.join(scenario['summary']['providers'])}")
    print(f"Resource Types: {', '.join(scenario['summary']['resource_types'])}")

    # Show sample resource
    if scenario['resources']:
        sample = scenario['resources'][0]
        print("\n📦 Sample Resource:")
        print(f"  Name: {sample.name}")
        print(f"  Provider: {sample.provider.value}")
        print(f"  Type: {sample.resource_type.value}")
        print(f"  Region: {sample.region}")
        print(f"  Tags: {sample.tags}")


def example_provider_specific():
    """Example of provider-specific data generation"""
    print("\n🔄 Provider-Specific Data Generation Example")
    print("=" * 50)

    generator = MultiCloudDataGenerator(seed=123)

    # Generate AWS-specific resources
    aws_resources = []
    for _ in range(5):
        resource = generator.generate_single_resource(
            CloudProvider.AWS,
            ResourceType.COMPUTE_INSTANCE
        )
        aws_resources.append(resource)

    print(f"Generated {len(aws_resources)} AWS EC2 instances:")
    for i, resource in enumerate(aws_resources[:3]):  # Show first 3
        print(f"  {i+1}. {resource.name} ({resource.resource_id}) - {resource.region}")


def example_cost_analysis():
    """Example of cost analysis with synthetic data"""
    print("\n🔄 Cost Analysis Example")
    print("=" * 50)

    generator = MultiCloudDataGenerator(seed=456)

    # Generate resources and cost data
    resources = generator.generate_resources(count=10)
    cost_entries = generator.generate_cost_entries(resources, days=30)

    # Calculate costs by provider
    provider_costs = {}
    for ce in cost_entries:
        provider = ce.provider.value
        provider_costs[provider] = provider_costs.get(provider, 0) + ce.cost

    print("💰 Cost Analysis by Provider:")
    for provider, cost in provider_costs.items():
        print(".2f")

    # Find highest cost resource
    resource_costs = {}
    for ce in cost_entries:
        resource_costs[ce.resource_id] = resource_costs.get(ce.resource_id, 0) + ce.cost

    highest_cost_resource_id = max(resource_costs, key=resource_costs.get)
    highest_cost = resource_costs[highest_cost_resource_id]

    # Find the resource details
    resource_details = next((r for r in resources if r.id == highest_cost_resource_id), None)
    if resource_details:
        print("\n🏆 Highest Cost Resource:")
        print(f"  Name: {resource_details.name}")
        print(f"  Provider: {resource_details.provider.value}")
        print(f"  Type: {resource_details.resource_type.value}")
        print(f"  Monthly Cost: ${highest_cost:.2f}")


def example_usage_patterns():
    """Example of usage pattern analysis"""
    print("\n🔄 Usage Pattern Analysis Example")
    print("=" * 50)

    generator = MultiCloudDataGenerator(seed=789)

    # Generate resources and usage patterns
    resources = generator.generate_resources(count=5)
    usage_patterns = generator.generate_usage_patterns(resources, days=3)

    # Analyze CPU utilization patterns
    cpu_utilizations = [up.cpu_utilization for up in usage_patterns]

    print("⚡ CPU Utilization Analysis:")
    print(f"  Average: {sum(cpu_utilizations)/len(cpu_utilizations):.1f}%")
    print(f"  Minimum: {min(cpu_utilizations):.1f}%")
    print(f"  Maximum: {max(cpu_utilizations):.1f}%")

    # Group by hour of day
    hourly_cpu = {}
    for up in usage_patterns:
        hour = up.date.hour
        if hour not in hourly_cpu:
            hourly_cpu[hour] = []
        hourly_cpu[hour].append(up.cpu_utilization)

    print("\n📊 Average CPU by Hour:")
    for hour in sorted(hourly_cpu.keys())[:5]:  # Show first 5 hours
        avg_cpu = sum(hourly_cpu[hour]) / len(hourly_cpu[hour])
        print(f"  Hour {hour:02d}: {avg_cpu:.1f}%")


def example_test_integration():
    """Example of how to use synthetic data in tests"""
    print("\n🔄 Test Integration Example")
    print("=" * 50)

    # Simulate test setup
    print("🧪 Setting up test environment...")

    # Generate test data
    generator = MultiCloudDataGenerator(seed=999)
    resources = generator.generate_resources(count=3)
    cost_entries = generator.generate_cost_entries(resources, days=7)

    print(f"✅ Generated {len(resources)} test resources")
    print(f"✅ Generated {len(cost_entries)} test cost entries")

    # Simulate test assertions
    print("\n🧪 Running test assertions...")

    # Test 1: All resources have required fields
    assert all(r.id and r.name and r.provider for r in resources), "Resources missing required fields"
    print("✅ Test 1 passed: All resources have required fields")

    # Test 2: Cost entries are positive
    assert all(ce.cost >= 0 for ce in cost_entries), "Cost entries must be non-negative"
    print("✅ Test 2 passed: All cost entries are non-negative")

    # Test 3: Providers are valid
    valid_providers = {CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE}
    resource_providers = {r.provider for r in resources}
    assert resource_providers.issubset(valid_providers), "Invalid provider found"
    print("✅ Test 3 passed: All providers are valid")

    print("\n🎉 All tests passed!")


def main():
    """Run all examples"""
    print("🚀 Cloud Cost Optimizer - Synthetic Data Examples")
    print("=" * 60)

    try:
        example_basic_generation()
        example_provider_specific()
        example_cost_analysis()
        example_usage_patterns()
        example_test_integration()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("\n📚 Next Steps:")
        print("   • Use synthetic_data/generator.py for custom data generation")
        print("   • Use synthetic_data/test_utils.py for test fixtures")
        print("   • Load generated JSON files for integration tests")
        print("   • Customize scenarios in generate_data.py")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
