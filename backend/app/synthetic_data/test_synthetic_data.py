"""
Unit Tests for Cloud Cost Optimizer using Synthetic Data

This module demonstrates how to use the synthetic data generators
in pytest unit tests for the Cloud Cost Optimizer application.
"""

import pytest
from datetime import datetime, timedelta
from synthetic_data.generator import MultiCloudDataGenerator, CloudProvider, ResourceType
from synthetic_data.test_utils import (
    SyntheticDataLoader,
    filter_resources_by_provider,
    calculate_total_cost,
    generate_test_resource
)


class TestSyntheticDataGeneration:
    """Test synthetic data generation functionality"""

    @pytest.fixture
    def generator(self):
        """Fixture for MultiCloudDataGenerator with fixed seed"""
        return MultiCloudDataGenerator(seed=42)

    @pytest.fixture
    def sample_resources(self, generator):
        """Fixture for sample resources"""
        return generator.generate_resources(count=10)

    def test_generate_resources_count(self, generator):
        """Test that generate_resources creates the correct number of resources"""
        resources = generator.generate_resources(count=5)
        assert len(resources) == 5

    def test_generate_resources_have_required_fields(self, sample_resources):
        """Test that all generated resources have required fields"""
        for resource in sample_resources:
            assert resource.id is not None
            assert resource.name is not None
            assert resource.provider in [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]
            assert resource.resource_type is not None
            assert resource.region is not None

    def test_generate_resources_unique_ids(self, sample_resources):
        """Test that all resources have unique IDs"""
        ids = [r.id for r in sample_resources]
        assert len(ids) == len(set(ids))

    def test_generate_cost_entries(self, generator, sample_resources):
        """Test cost entry generation"""
        cost_entries = generator.generate_cost_entries(sample_resources, days=7)

        # Should have cost entries for each resource and day (inclusive of start and end)
        expected_count = len(sample_resources) * 8  # 7 days + 1 (inclusive range)
        assert len(cost_entries) == expected_count

        # All costs should be positive
        assert all(ce.cost >= 0 for ce in cost_entries)

    def test_generate_usage_patterns(self, generator, sample_resources):
        """Test usage pattern generation"""
        usage_patterns = generator.generate_usage_patterns(sample_resources, days=3)

        # Should have usage patterns for each resource, day, and hour (24 per day)
        # Note: days=3 generates 4 days of data (inclusive range: day 0, 1, 2, 3)
        expected_count = len(sample_resources) * 4 * 24
        assert len(usage_patterns) == expected_count

        # CPU utilization should be between 0 and 100
        assert all(0 <= up.cpu_utilization <= 100 for up in usage_patterns)


class TestMultiCloudScenarios:
    """Test multi-cloud scenario generation"""

    @pytest.fixture
    def generator(self):
        return MultiCloudDataGenerator(seed=123)

    def test_balanced_scenario(self, generator):
        """Test balanced multi-cloud scenario"""
        scenario = generator.generate_multi_cloud_scenario("balanced")

        assert scenario['scenario_type'] == 'balanced'
        assert len(scenario['resources']) > 0
        assert len(scenario['cost_entries']) > 0
        assert len(scenario['usage_patterns']) > 0

        # Check that all three providers are represented
        providers = set(r.provider for r in scenario['resources'])
        assert providers == {CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE}

    def test_provider_specific_scenario(self, generator):
        """Test provider-specific scenarios"""
        # Generate AWS-specific resources directly
        aws_resources = []
        for _ in range(20):
            resource = generator.generate_single_resource(CloudProvider.AWS, ResourceType.COMPUTE_INSTANCE)
            aws_resources.append(resource)

        # Generate some non-AWS resources
        other_resources = generator.generate_resources(count=10)
        non_aws_resources = [r for r in other_resources if r.provider != CloudProvider.AWS]

        # Combine to create an AWS-heavy scenario
        all_resources = aws_resources + non_aws_resources[:5]  # Add just 5 non-AWS

        aws_count = sum(1 for r in all_resources if r.provider == CloudProvider.AWS)

        # AWS should be the majority provider
        assert aws_count > len(all_resources) * 0.5


class TestCostOptimizationLogic:
    """Test cost optimization logic using synthetic data"""

    @pytest.fixture
    def generator(self):
        return MultiCloudDataGenerator(seed=456)

    def test_cost_calculation_accuracy(self, generator):
        """Test that cost calculations are accurate"""
        resources = generator.generate_resources(count=5)
        cost_entries = generator.generate_cost_entries(resources, days=30)

        # Calculate total cost manually
        manual_total = sum(ce.cost for ce in cost_entries)

        # Calculate using utility function
        utility_total = calculate_total_cost(cost_entries)

        assert abs(manual_total - utility_total) < 0.01

    def test_provider_cost_filtering(self, generator):
        """Test filtering resources by provider"""
        resources = generator.generate_resources(count=20)

        aws_resources = filter_resources_by_provider(resources, CloudProvider.AWS)
        gcp_resources = filter_resources_by_provider(resources, CloudProvider.GCP)
        azure_resources = filter_resources_by_provider(resources, CloudProvider.AZURE)

        # All filtered resources should have the correct provider
        assert all(r.provider == CloudProvider.AWS for r in aws_resources)
        assert all(r.provider == CloudProvider.GCP for r in gcp_resources)
        assert all(r.provider == CloudProvider.AZURE for r in azure_resources)

        # Total should equal original count
        assert len(aws_resources) + len(gcp_resources) + len(azure_resources) == len(resources)


class TestResourceTypeAnalysis:
    """Test analysis by resource type"""

    @pytest.fixture
    def generator(self):
        return MultiCloudDataGenerator(seed=789)

    def test_resource_type_distribution(self, generator):
        """Test that resource types are distributed properly"""
        resources = generator.generate_resources(count=50)

        resource_types = [r.resource_type for r in resources]
        unique_types = set(resource_types)

        # Should have multiple resource types
        assert len(unique_types) > 1

        # Each type should appear at least once
        for resource_type in ResourceType:
            assert resource_type in unique_types

    def test_compute_resource_costs(self, generator):
        """Test costs for compute resources specifically"""
        resources = generator.generate_resources(count=20)
        compute_resources = [r for r in resources if r.resource_type == ResourceType.COMPUTE_INSTANCE]

        if compute_resources:
            cost_entries = generator.generate_cost_entries(compute_resources, days=7)

            # Compute resources should have reasonable costs
            avg_daily_cost = sum(ce.cost for ce in cost_entries) / len(cost_entries)
            assert 5 <= avg_daily_cost <= 50  # Reasonable range for compute instances


class TestDataPersistence:
    """Test loading and using persisted synthetic data"""

    def test_load_from_json(self, tmp_path):
        """Test loading synthetic data from JSON file"""
        # Create a temporary JSON file with synthetic data
        generator = MultiCloudDataGenerator(seed=999)
        resources = generator.generate_resources(count=3)

        # Manually create JSON data
        import json
        json_data = []
        for resource in resources:
            resource_dict = {
                'id': resource.id,
                'provider': resource.provider.value,
                'resource_id': resource.resource_id,
                'resource_type': resource.resource_type.value,
                'name': resource.name,
                'region': resource.region,
                'tags': resource.tags,
                'specifications': resource.specifications,
                'created_at': resource.created_at.isoformat() if resource.created_at else None,
                'updated_at': resource.updated_at.isoformat() if resource.updated_at else None
            }
            json_data.append(resource_dict)

        # Save to temporary file
        json_file = tmp_path / "test_resources.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f)

        # Load using SyntheticDataLoader
        data_loader = SyntheticDataLoader(tmp_path)
        loaded_resources = data_loader.load_resources("test_resources.json")

        assert len(loaded_resources) == len(resources)
        assert all(r.id == lr.id for r, lr in zip(resources, loaded_resources))


class TestIntegrationScenarios:
    """Test integration scenarios with synthetic data"""

    @pytest.fixture
    def generator(self):
        return MultiCloudDataGenerator(seed=111)

    def test_full_workflow_simulation(self, generator):
        """Test a complete workflow from resource creation to cost analysis"""
        # 1. Generate resources
        resources = generator.generate_resources(count=15)

        # 2. Generate cost data for a month
        cost_entries = generator.generate_cost_entries(resources, days=30)

        # 3. Generate usage patterns
        usage_patterns = generator.generate_usage_patterns(resources, days=30)

        # 4. Perform analysis
        total_cost = calculate_total_cost(cost_entries)
        provider_breakdown = {}

        for ce in cost_entries:
            provider = ce.provider.value
            provider_breakdown[provider] = provider_breakdown.get(provider, 0) + ce.cost

        # Assertions
        assert total_cost > 0
        assert len(provider_breakdown) >= 1  # At least one provider
        assert len(usage_patterns) == len(resources) * 31 * 24  # 31 days (inclusive) * 24 hours per day

        # Check that usage patterns have realistic values
        cpu_values = [up.cpu_utilization for up in usage_patterns]
        assert 0 <= min(cpu_values) <= max(cpu_values) <= 100


if __name__ == "__main__":
    pytest.main([__file__])
