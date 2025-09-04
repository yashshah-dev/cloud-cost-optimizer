#!/usr/bin/env python3
"""
Load and Demonstrate Synthetic Data Usage

This script demonstrates how to load and use the realistic synthetic data
generated for the Cloud Cost Optimizer application.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add the synthetic_data directory to the path
sys.path.append(str(Path(__file__).parent))

from synthetic_data.test_utils import SyntheticDataLoader
from synthetic_data.generator import CloudProvider, ResourceType


def load_balanced_scenario():
    """Load and display the balanced multi-cloud scenario"""
    print("🔄 Loading Balanced Multi-Cloud Scenario")
    print("=" * 50)

    # Set the correct data directory
    data_dir = Path(__file__).parent / "synthetic_data" / "datasets"
    loader = SyntheticDataLoader(data_dir)

    try:
        # Load complete scenario
        scenario_data = loader.load_json("balanced_complete.json")

        print(f"Scenario Type: {scenario_data.get('scenario_type', 'N/A')}")
        print(f"Total Resources: {scenario_data.get('summary', {}).get('total_resources', 0)}")
        print(f"Total Cost: ${scenario_data.get('summary', {}).get('total_cost', 0):.2f}")
        print(f"Providers: {', '.join(scenario_data.get('summary', {}).get('providers', []))}")
        print(f"Resource Types: {', '.join(scenario_data.get('summary', {}).get('resource_types', []))}")

        # Load individual components
        resources = loader.load_resources("balanced_resources.json")
        cost_entries = loader.load_cost_entries("balanced_cost_entries.json")
        usage_patterns = loader.load_usage_patterns("balanced_usage_patterns.json")

        print("\n📊 Detailed Breakdown:")
        print(f"  Resources loaded: {len(resources)}")
        print(f"  Cost entries: {len(cost_entries)}")
        print(f"  Usage patterns: {len(usage_patterns)}")

        return resources, cost_entries, usage_patterns

    except FileNotFoundError as e:
        print(f"❌ Error loading balanced scenario: {e}")
        return [], [], []
        print(f"❌ Error loading balanced scenario: {e}")
        return [], [], []


def load_provider_specific_data():
    """Load and compare provider-specific datasets"""
    print("\n🔄 Loading Provider-Specific Data")
    print("=" * 50)

    # Set the correct data directory
    data_dir = Path(__file__).parent / "synthetic_data" / "datasets"
    loader = SyntheticDataLoader(data_dir)
    providers_data = {}

    for provider_name, provider_enum in [("AWS", CloudProvider.AWS),
                                        ("GCP", CloudProvider.GCP),
                                        ("Azure", CloudProvider.AZURE)]:
        try:
            resources = loader.load_resources(f"{provider_name.lower()}_resources.json")
            cost_entries = loader.load_cost_entries(f"{provider_name.lower()}_cost_entries.json")
            usage_patterns = loader.load_usage_patterns(f"{provider_name.lower()}_usage_patterns.json")

            providers_data[provider_name] = {
                'resources': resources,
                'cost_entries': cost_entries,
                'usage_patterns': usage_patterns
            }

            print(f"{provider_name}:")
            print(f"  Resources: {len(resources)}")
            print(f"  Cost entries: {len(cost_entries)}")
            print(f"  Usage patterns: {len(usage_patterns)}")

            if resources:
                total_cost = sum(ce.cost for ce in cost_entries)
                print(".2f")

        except FileNotFoundError as e:
            print(f"❌ Error loading {provider_name} data: {e}")

    return providers_data


def load_test_scenarios():
    """Load different test scenario sizes"""
    print("\n🔄 Loading Test Scenarios")
    print("=" * 50)

    # Set the correct data directory
    data_dir = Path(__file__).parent / "synthetic_data" / "datasets"
    loader = SyntheticDataLoader(data_dir)
    scenarios = {}

    for size in ["minimal", "small", "medium"]:
        try:
            scenario_data = loader.load_json(f"test_{size}.json")
            scenarios[size] = scenario_data

            print(f"{size.capitalize()}: {scenario_data.get('summary', {}).get('total_resources', 0)} resources")

        except FileNotFoundError as e:
            print(f"❌ Error loading {size} scenario: {e}")

    return scenarios


def analyze_loaded_data(resources, cost_entries, usage_patterns):
    """Analyze and display insights from loaded data"""
    print("\n🔍 Data Analysis")
    print("=" * 50)

    if not resources:
        print("No data to analyze")
        return

    # Provider distribution
    provider_counts = {}
    for r in resources:
        provider = r.provider.value
        provider_counts[provider] = provider_counts.get(provider, 0) + 1

    print("🌐 Provider Distribution:")
    for provider, count in provider_counts.items():
        percentage = (count / len(resources)) * 100
        print(".1f")

    # Resource type distribution
    type_counts = {}
    for r in resources:
        rtype = r.resource_type.value
        type_counts[rtype] = type_counts.get(rtype, 0) + 1

    print("\n🏗️  Resource Type Distribution:")
    for rtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(resources)) * 100
        print(".1f")

    # Cost analysis
    if cost_entries:
        total_cost = sum(ce.cost for ce in cost_entries)
        avg_daily_cost = total_cost / len(cost_entries) if cost_entries else 0

        print("\n💰 Cost Analysis:")
        print(".2f")
        print(".2f")

        # Cost by provider
        provider_costs = {}
        for ce in cost_entries:
            provider_costs[ce.provider.value] = provider_costs.get(ce.provider.value, 0) + ce.cost

        print("  Cost by Provider:")
        for provider, cost in provider_costs.items():
            percentage = (cost / total_cost) * 100
            print(".1f")

    # Usage patterns analysis
    if usage_patterns:
        cpu_values = [up.cpu_utilization for up in usage_patterns]
        memory_values = [up.memory_utilization for up in usage_patterns]

        print("\n⚡ Usage Patterns (Sample):")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".1f")


def demonstrate_data_usage(resources, cost_entries, usage_patterns):
    """Demonstrate practical usage of the loaded data"""
    print("\n🚀 Practical Usage Examples")
    print("=" * 50)

    if not resources:
        print("No data available for demonstration")
        return

    # Example 1: Find highest cost resource
    if cost_entries:
        resource_costs = {}
        for ce in cost_entries:
            resource_costs[ce.resource_id] = resource_costs.get(ce.resource_id, 0) + ce.cost

        if resource_costs:
            highest_cost_id = max(resource_costs, key=resource_costs.get)
            highest_cost = resource_costs[highest_cost_id]

            # Find the resource details
            resource_details = next((r for r in resources if r.id == highest_cost_id), None)
            if resource_details:
                print("🏆 Highest Cost Resource:")
                print(f"  Name: {resource_details.name}")
                print(f"  Provider: {resource_details.provider.value}")
                print(f"  Type: {resource_details.resource_type.value}")
                print(".2f")

    # Example 2: Resources by region
    region_counts = {}
    for r in resources:
        region_counts[r.region] = region_counts.get(r.region, 0) + 1

    if region_counts:
        print("\n📍 Top Regions:")
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {region}: {count} resources")

    # Example 3: Recent activity (if timestamps available)
    if resources and hasattr(resources[0], 'created_at') and resources[0].created_at:
        print("\n📅 Recent Resources (last 30 days):")
        recent_count = 0
        for r in resources:
            if r.created_at:
                days_old = (datetime.now() - r.created_at.replace(tzinfo=None)).days
                if days_old <= 30:
                    recent_count += 1
        print(f"  {recent_count} resources created recently")


def main():
    """Main function to load and demonstrate synthetic data"""
    print("🚀 Cloud Cost Optimizer - Synthetic Data Loader")
    print("=" * 60)

    try:
        # Load balanced scenario
        resources, cost_entries, usage_patterns = load_balanced_scenario()

        # Load provider-specific data
        provider_data = load_provider_specific_data()

        # Load test scenarios
        test_scenarios = load_test_scenarios()

        # Analyze the data
        analyze_loaded_data(resources, cost_entries, usage_patterns)

        # Demonstrate usage
        demonstrate_data_usage(resources, cost_entries, usage_patterns)

        print("\n" + "=" * 60)
        print("✅ Synthetic data loaded successfully!")
        print("\n📚 Available Datasets:")
        print("   • Balanced multi-cloud scenario")
        print("   • Provider-specific datasets (AWS, GCP, Azure)")
        print("   • Test scenarios (minimal, small, medium)")
        print("   • Complete datasets with resources, costs, and usage patterns")
        print("\n🔧 Usage in Code:")
        print("   from synthetic_data.test_utils import SyntheticDataLoader")
        print("   data_dir = Path('synthetic_data/datasets')")
        print("   loader = SyntheticDataLoader(data_dir)")
        print("   resources = loader.load_resources('balanced_resources.json')")

    except Exception as e:
        print(f"\n❌ Error loading synthetic data: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
