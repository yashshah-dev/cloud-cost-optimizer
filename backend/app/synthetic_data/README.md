# Synthetic Data Generators for Multi-Cloud Testing

This directory contains synthetic data generators for testing the Cloud Cost Optimizer across multiple cloud providers (AWS, GCP, Azure). These generators create realistic datasets with resources, cost entries, and usage patterns for comprehensive testing.

## 📁 Files Overview

- **`generator.py`** - Main synthetic data generator with classes and methods
- **`generate_data.py`** - Script to generate and save datasets to JSON files
- **`test_utils.py`** - Test utilities and pytest fixtures for using synthetic data
- **`__init__.py`** - Package initialization

## 🚀 Quick Start

### Generate Synthetic Data

```bash
# Navigate to the synthetic data directory
cd backend/app/synthetic_data

# Generate all datasets
python generate_data.py

# Generate specific scenarios
python generate_data.py --scenarios balanced aws_heavy cost_anomaly

# Generate with custom output directory
python generate_data.py --output-dir ./test_data --seed 12345
```

### Use in Python Code

```python
from synthetic_data.generator import MultiCloudDataGenerator, CloudProvider

# Create generator
generator = MultiCloudDataGenerator(seed=42)

# Generate balanced multi-cloud scenario
scenario = generator.generate_multi_cloud_scenario("balanced")

print(f"Generated {scenario['summary']['total_resources']} resources")
print(f"Total cost: ${scenario['summary']['total_cost']:.2f}")

# Access individual components
resources = scenario['resources']
cost_entries = scenario['cost_entries']
usage_patterns = scenario['usage_patterns']
```

### Use in Tests

```python
import pytest
from synthetic_data.test_utils import synthetic_data_loader, multi_cloud_resources

def test_cost_optimization(multi_cloud_resources):
    """Test cost optimization with multi-cloud data"""
    # Your test logic here
    assert len(multi_cloud_resources) > 0

def test_provider_filtering(synthetic_data_loader):
    """Test filtering resources by provider"""
    aws_resources = synthetic_data_loader.load_resources("aws_resources.json")
    assert all(r.provider.value == "aws" for r in aws_resources)
```

## 📊 Generated Datasets

The generator creates several types of datasets:

### Scenario Types
- **`balanced`** - Equal distribution across AWS, GCP, Azure
- **`aws_heavy`** - Mostly AWS resources with some others
- **`cost_anomaly`** - Includes high-cost resources for anomaly testing

### Test Sizes
- **`minimal`** - 5 resources (quick unit tests)
- **`small`** - 15 resources (unit tests)
- **`medium`** - 50 resources (integration tests)
- **`large`** - 100 resources (performance tests)

### Provider-Specific
- **`aws_resources.json`** - AWS-only resources
- **`gcp_resources.json`** - GCP-only resources
- **`azure_resources.json`** - Azure-only resources

## 🏗️ Data Structure

### Resources
```python
{
    "id": "uuid",
    "provider": "aws|gcp|azure",
    "resource_id": "provider-specific-id",
    "resource_type": "compute|database|storage|network|container|serverless",
    "name": "human-readable-name",
    "region": "us-east-1",
    "tags": {"Environment": "production", "Team": "backend"},
    "specifications": {"instance_type": "t3.medium", "vcpus": 2},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### Cost Entries
```python
{
    "id": "uuid",
    "resource_id": "resource-uuid",
    "provider": "aws|gcp|azure",
    "service": "compute|database|storage",
    "cost": 15.50,
    "currency": "USD",
    "date": "2024-01-01",
    "region": "us-east-1",
    "tags": {"Environment": "production"}
}
```

### Usage Patterns
```python
{
    "resource_id": "resource-uuid",
    "date": "2024-01-01T10:00:00",
    "cpu_utilization": 65.5,
    "memory_utilization": 70.2,
    "network_in": 25.3,
    "network_out": 30.1,
    "storage_used": 45.8,
    "requests_per_minute": 120.5  # Optional, for serverless
}
```

## 🎯 Use Cases

### Unit Testing
```python
def test_resource_creation():
    resource = generate_test_resource()
    assert validate_resource_data(resource)
```

### Integration Testing
```python
def test_cost_aggregation(medium_dataset):
    total_cost = calculate_total_cost(medium_dataset['cost_entries'])
    assert total_cost > 0
```

### E2E Testing
```python
def test_multi_cloud_dashboard(balanced_scenario):
    # Test dashboard with multi-cloud data
    resources = balanced_scenario['resources']
    providers = set(r.provider.value for r in resources)
    assert len(providers) >= 2  # At least 2 cloud providers
```

### Performance Testing
```python
def test_large_dataset_performance():
    large_dataset = generate_large_dataset("large")
    start_time = time.time()
    # Perform expensive operations
    total_cost = calculate_total_cost(large_dataset['cost_entries'])
    duration = time.time() - start_time
    assert duration < 5.0  # Should complete within 5 seconds
```

## 🔧 Customization

### Custom Scenarios
```python
# Create custom scenario
generator = MultiCloudDataGenerator(seed=42)

# Generate resources with specific distribution
aws_resources = [generator.generate_single_resource(CloudProvider.AWS, ResourceType.COMPUTE_INSTANCE)
                 for _ in range(20)]
gcp_resources = [generator.generate_single_resource(CloudProvider.GCP, ResourceType.STORAGE)
                 for _ in range(10)]

all_resources = aws_resources + gcp_resources
```

### Realistic Patterns
The generator includes:
- **Seasonal variations** - Higher costs during business hours/weekdays
- **Regional differences** - Cost variations by region
- **Resource-specific costs** - Different pricing for different instance types
- **Usage patterns** - Time-of-day utilization variations
- **Tag-based organization** - Realistic tagging patterns

## 📈 Metrics & Validation

### Data Quality Checks
- All resources have valid provider/resource type combinations
- Cost entries have realistic values and date ranges
- Usage patterns include time-of-day variations
- Cross-references between resources and cost entries are valid

### Performance Benchmarks
- Generation speed: ~1000 resources/second
- Memory usage: ~50MB for large datasets
- File sizes: ~10MB for comprehensive scenarios

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests** - Individual functions with minimal data
2. **Integration Tests** - Component interactions with medium datasets
3. **E2E Tests** - Full workflows with balanced scenarios
4. **Performance Tests** - Large datasets for scalability validation
5. **Anomaly Tests** - Edge cases and unusual patterns

### CI/CD Integration
```yaml
# Example GitHub Actions step
- name: Generate Test Data
  run: |
    cd backend/app/synthetic_data
    python generate_data.py --scenarios balanced minimal

- name: Run Tests with Synthetic Data
  run: |
    pytest tests/ -v --cov=app
```

## 📚 Examples

See `example_test_data.json` for sample output format.

For more advanced usage, check the docstrings in `generator.py` and `test_utils.py`.

## 🤝 Contributing

When adding new data patterns:
1. Update the generator classes in `generator.py`
2. Add corresponding test utilities in `test_utils.py`
3. Update this README with new examples
4. Regenerate test datasets with `python generate_data.py`

---

**Need Help?** Check the docstrings in the code files or create an issue in the main repository.
