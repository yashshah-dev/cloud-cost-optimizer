#!/usr/bin/env python3
"""
Synthetic Data Generation Script

This script generates and saves synthetic multi-cloud data for testing the Cloud Cost Optimizer.
It creates realistic datasets with resources, cost entries, and usage patterns across AWS, GCP, and Azure.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from synthetic_data.generator import MultiCloudDataGenerator, CloudProvider


def save_to_json(data: Any, filename: str, output_dir: Path) -> None:
    """Save data to a JSON file"""
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"✅ Saved {filename} ({filepath.stat().st_size} bytes)")


def generate_and_save_scenario(generator: MultiCloudDataGenerator, scenario_type: str,
                             output_dir: Path) -> None:
    """Generate and save a complete scenario"""
    print(f"\n🔄 Generating {scenario_type} scenario...")

    scenario = generator.generate_multi_cloud_scenario(scenario_type)

    # Save individual components
    save_to_json(
        [r.__dict__ for r in scenario['resources']],
        f"{scenario_type}_resources.json",
        output_dir
    )

    save_to_json(
        [ce.__dict__ for ce in scenario['cost_entries']],
        f"{scenario_type}_cost_entries.json",
        output_dir
    )

    save_to_json(
        [up.__dict__ for up in scenario['usage_patterns']],
        f"{scenario_type}_usage_patterns.json",
        output_dir
    )

    # Save summary
    save_to_json(scenario['summary'], f"{scenario_type}_summary.json", output_dir)

    # Save complete scenario
    save_to_json(scenario, f"{scenario_type}_complete.json", output_dir)

    print(f"📊 {scenario_type.title()} Scenario Summary:")
    print(f"   • Resources: {scenario['summary']['total_resources']}")
    print(f"   • Cost Entries: {len(scenario['cost_entries'])}")
    print(f"   • Usage Patterns: {len(scenario['usage_patterns'])}")
    print(f"   • Total Cost: ${scenario['summary']['total_cost']:.2f}")
    print(f"   • Providers: {', '.join(scenario['summary']['providers'])}")


def generate_provider_specific_data(generator: MultiCloudDataGenerator, output_dir: Path) -> None:
    """Generate provider-specific datasets"""
    print("\n🔄 Generating provider-specific datasets...")

    providers = [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]

    for provider in providers:
        print(f"\n📦 Generating {provider.value.upper()} data...")

        # Generate resources for this provider by filtering from a larger set
        all_resources = generator.generate_resources(count=50)  # Generate more than needed
        resources = [r for r in all_resources if r.provider == provider][:25]  # Take first 25

        # Generate cost entries
        cost_entries = generator.generate_cost_entries(resources, days=30)

        # Generate usage patterns
        usage_patterns = generator.generate_usage_patterns(resources, days=7)

        # Save data
        save_to_json(
            [r.__dict__ for r in resources],
            f"{provider.value}_resources.json",
            output_dir
        )

        save_to_json(
            [ce.__dict__ for ce in cost_entries],
            f"{provider.value}_cost_entries.json",
            output_dir
        )

        save_to_json(
            [up.__dict__ for up in usage_patterns],
            f"{provider.value}_usage_patterns.json",
            output_dir
        )

        total_cost = sum(ce.cost for ce in cost_entries)
        print(f"   • {provider.value.upper()}: {len(resources)} resources, ${total_cost:.2f} total cost")


def generate_test_scenarios(generator: MultiCloudDataGenerator, output_dir: Path) -> None:
    """Generate specific test scenarios"""
    print("\n🔄 Generating test scenarios...")

    scenarios = [
        ("minimal", 5),      # Small dataset for quick tests
        ("small", 15),       # Small dataset for unit tests
        ("medium", 50),      # Medium dataset for integration tests
        ("large", 100),      # Large dataset for performance tests
    ]

    for scenario_name, resource_count in scenarios:
        print(f"\n📊 Generating {scenario_name} test scenario ({resource_count} resources)...")

        resources = generator.generate_resources(count=resource_count)
        cost_entries = generator.generate_cost_entries(resources, days=30)
        usage_patterns = generator.generate_usage_patterns(resources, days=7)

        scenario_data = {
            "scenario": scenario_name,
            "resources": [r.__dict__ for r in resources],
            "cost_entries": [ce.__dict__ for ce in cost_entries],
            "usage_patterns": [up.__dict__ for up in usage_patterns],
            "summary": {
                "total_resources": len(resources),
                "total_cost_entries": len(cost_entries),
                "total_usage_patterns": len(usage_patterns),
                "total_cost": sum(ce.cost for ce in cost_entries),
                "date_range": "30 days",
                "providers": list(set(r.provider.value for r in resources))
            }
        }

        save_to_json(scenario_data, f"test_{scenario_name}.json", output_dir)

        print(f"   • Resources: {len(resources)}")
        print(f"   • Cost entries: {len(cost_entries)}")
        print(f"   • Usage patterns: {len(usage_patterns)}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic multi-cloud data for testing")
    parser.add_argument("--output-dir", "-o", default="./synthetic_data",
                       help="Output directory for generated data")
    parser.add_argument("--seed", "-s", type=int, default=42,
                       help="Random seed for reproducible results")
    parser.add_argument("--scenarios", nargs="*", default=["balanced", "aws_heavy", "cost_anomaly"],
                       help="Scenario types to generate")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("🚀 Cloud Cost Optimizer - Synthetic Data Generator")
    print("=" * 50)
    print(f"Output Directory: {output_dir.absolute()}")
    print(f"Random Seed: {args.seed}")
    print(f"Scenarios: {', '.join(args.scenarios)}")
    print()

    # Initialize generator
    generator = MultiCloudDataGenerator(seed=args.seed)

    # Generate main scenarios
    for scenario_type in args.scenarios:
        generate_and_save_scenario(generator, scenario_type, output_dir)

    # Generate provider-specific data
    generate_provider_specific_data(generator, output_dir)

    # Generate test scenarios
    generate_test_scenarios(generator, output_dir)

    print("\n" + "=" * 50)
    print("✅ Synthetic data generation complete!")
    print(f"📁 Data saved to: {output_dir.absolute()}")
    print("\n📋 Generated files:")
    for file in sorted(output_dir.glob("*.json")):
        print(f"   • {file.name}")

    print("\n🎯 Use these datasets for:")
    print("   • Unit testing: test_minimal.json, test_small.json")
    print("   • Integration testing: test_medium.json")
    print("   • Performance testing: test_large.json")
    print("   • Multi-cloud scenarios: balanced_complete.json")
    print("   • Provider-specific tests: aws_resources.json, gcp_resources.json, azure_resources.json")


if __name__ == "__main__":
    main()
