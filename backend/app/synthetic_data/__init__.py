"""
Synthetic Data Generators for Cloud Cost Optimizer Testing

This package provides realistic synthetic data generation for testing
the Cloud Cost Optimizer across multiple cloud providers.
"""

from .generator import (
    MultiCloudDataGenerator,
    CloudProvider,
    ResourceType,
    SyntheticResource,
    SyntheticCostEntry,
    SyntheticUsagePattern,
    generate_aws_resources,
    generate_gcp_resources,
    generate_azure_resources,
    generate_multi_cloud_dataset
)

from .test_utils import (
    SyntheticDataLoader,
    filter_resources_by_provider,
    filter_resources_by_type,
    get_cost_entries_for_resource,
    calculate_total_cost,
    get_usage_patterns_for_resource,
    generate_test_resource,
    generate_test_cost_entries,
    validate_resource_data,
    validate_cost_entry_data,
    validate_usage_pattern_data,
    generate_large_dataset
)

__version__ = "1.0.0"
__all__ = [
    # Main generator classes
    "MultiCloudDataGenerator",
    "SyntheticDataLoader",

    # Enums
    "CloudProvider",
    "ResourceType",

    # Data classes
    "SyntheticResource",
    "SyntheticCostEntry",
    "SyntheticUsagePattern",

    # Convenience functions
    "generate_aws_resources",
    "generate_gcp_resources",
    "generate_azure_resources",
    "generate_multi_cloud_dataset",

    # Test utilities
    "filter_resources_by_provider",
    "filter_resources_by_type",
    "get_cost_entries_for_resource",
    "calculate_total_cost",
    "get_usage_patterns_for_resource",
    "generate_test_resource",
    "generate_test_cost_entries",
    "validate_resource_data",
    "validate_cost_entry_data",
    "validate_usage_pattern_data",
    "generate_large_dataset"
]
