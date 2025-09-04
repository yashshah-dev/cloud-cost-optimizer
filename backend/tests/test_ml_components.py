#!/usr/bin/env python3
"""
Unit tests for Phase 2 ML components.
Tests UsagePatternAnalyzer, RiskAssessor, OptimizationRecommender, and PerformancePredictor.
"""

import unittest
import json
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch
import sys
import os
import pandas as pd

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.usage_analyzer import UsagePatternAnalyzer
from app.ml.risk_assessor import RiskAssessor
from app.ml.recommender import OptimizationRecommender
from app.ml.predictor import PerformancePredictor

class TestUsagePatternAnalyzer(unittest.TestCase):
    """Test cases for UsagePatternAnalyzer."""

    def setUp(self):
        self.analyzer = UsagePatternAnalyzer()

    def test_preprocess_data(self):
        """Test data preprocessing functionality."""
        # Sample usage data
        usage_data = [
            {
                'timestamp': '2024-01-01T10:00:00',
                'cpu_utilization': 50,
                'memory_utilization': 60,
                'network_in': 100,
                'network_out': 80
            },
            {
                'timestamp': '2024-01-01T11:00:00',
                'cpu_utilization': 55,
                'memory_utilization': 65,
                'network_in': 120,
                'network_out': 90
            }
        ]

        df = self.analyzer.preprocess_data(usage_data)

        # Check that required columns are present
        required_columns = ['cpu_utilization', 'memory_utilization', 'hour_of_day', 'day_of_week']
        for col in required_columns:
            self.assertIn(col, df.columns)

        # Check data types
        self.assertEqual(len(df), 2)
        self.assertTrue(isinstance(df.index, pd.DatetimeIndex))

    def test_detect_anomalies(self):
        """Test anomaly detection functionality."""
        # Create data with an obvious anomaly
        usage_data = [
            {
                'timestamp': f'2024-01-{day:02d}T10:00:00',
                'cpu_utilization': 50 if day != 15 else 95,  # Anomaly on day 15
                'memory_utilization': 60,
                'network_in': 100,
                'network_out': 80
            }
            for day in range(1, 31)
        ]

        anomalies = self.analyzer.detect_anomalies(usage_data, threshold=2.0)

        # Should detect the anomaly
        self.assertTrue(len(anomalies) > 0)
        anomaly_dates = [a['timestamp'][:10] for a in anomalies]  # Extract date part
        self.assertIn('2024-01-15', anomaly_dates)

    def test_train_model_insufficient_data(self):
        """Test model training with insufficient data."""
        usage_data = [{'timestamp': '2024-01-01T10:00:00', 'cpu_utilization': 50}]

        result = self.analyzer.train_model(usage_data)

        self.assertEqual(result['status'], 'insufficient_data')
        self.assertEqual(result['samples'], 1)

class TestRiskAssessor(unittest.TestCase):
    """Test cases for RiskAssessor."""

    def setUp(self):
        self.assessor = RiskAssessor()

    def test_assess_resource_criticality(self):
        """Test resource criticality assessment."""
        # Test critical resource
        critical_resource = {
            'resource_type': 'database',
            'name': 'prod-database-01',
            'tags': {'Environment': 'production'}
        }

        result = self.assessor._assess_resource_criticality(critical_resource)

        self.assertGreater(result['score'], 0.5)
        self.assertIn('Critical resource type', result['factors'])

    def test_assess_business_impact(self):
        """Test business impact assessment."""
        # Test high business impact resource
        business_resource = {
            'tags': {
                'Team': 'sales',
                'Project': 'customer-portal',
                'Environment': 'production'
            }
        }

        result = self.assessor._assess_business_impact(business_resource)

        self.assertGreater(result['score'], 0.3)
        self.assertTrue(len(result['factors']) > 0)

    def test_overall_risk_assessment(self):
        """Test complete risk assessment."""
        resource = {
            'resource_type': 'ec2',
            'name': 'web-server-prod',
            'tags': {'Environment': 'production', 'Team': 'engineering'}
        }

        optimization = {
            'type': 'rightsizing',
            'requires_downtime': True
        }

        result = self.assessor.assess_risk(resource, optimization)

        # Check required fields
        required_fields = ['overall_risk_score', 'risk_level', 'assessment_breakdown', 'recommendations']
        for field in required_fields:
            self.assertIn(field, result)

        # Check risk level is valid
        valid_levels = ['low', 'medium', 'high', 'critical']
        self.assertIn(result['risk_level'], valid_levels)

class TestOptimizationRecommender(unittest.TestCase):
    """Test cases for OptimizationRecommender."""

    def setUp(self):
        self.recommender = OptimizationRecommender()

    def test_analyze_rightsizing_underutilized(self):
        """Test rightsizing analysis for underutilized resource."""
        resource = {
            'id': 'test-resource-1',
            'instance_type': 't3.large',
            'resource_type': 'ec2'
        }

        usage_patterns = {
            'avg_cpu_utilization': 15,  # Underutilized
            'avg_memory_utilization': 20,
            'peak_cpu_utilization': 30  # Also underutilized
        }

        result = self.recommender._analyze_rightsizing(resource, usage_patterns)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'rightsizing')
        self.assertGreater(result['potential_savings'], 0)

    def test_analyze_reserved_instance(self):
        """Test reserved instance analysis."""
        resource = {
            'id': 'test-resource-2',
            'instance_type': 't3.medium',
            'resource_type': 'ec2'
        }

        # Mock cost data for 30+ days
        cost_data = [
            {
                'resource_id': 'test-resource-2',
                'cost': 20.0,
                'date': (datetime.now(UTC) - timedelta(days=i)).isoformat()
            }
            for i in range(35)
        ]

        result = self.recommender._analyze_reserved_instance(resource, cost_data)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'reserved_instance')
        self.assertGreater(result['potential_savings'], 0)

    def test_generate_recommendations(self):
        """Test complete recommendation generation."""
        resources = [
            {
                'id': 'test-1',
                'instance_type': 't3.large',
                'resource_type': 'ec2'
            }
        ]

        usage_patterns = {
            'test-1': {
                'avg_cpu_utilization': 15,  # Underutilized to trigger rightsizing
                'avg_memory_utilization': 20,
                'peak_cpu_utilization': 25
            }
        }

        cost_data = [
            {
                'resource_id': 'test-1',
                'cost': 30.0,
                                'date': datetime.now(UTC).isoformat()
            }
        ]

        recommendations = self.recommender.generate_recommendations(
            resources, usage_patterns, cost_data
        )

        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)

        # Check recommendation structure
        rec = recommendations[0]
        required_fields = ['id', 'type', 'title', 'potential_savings', 'confidence_score']
        for field in required_fields:
            self.assertIn(field, rec)

class TestPerformancePredictor(unittest.TestCase):
    """Test cases for PerformancePredictor."""

    def setUp(self):
        self.predictor = PerformancePredictor()

    def test_determine_workload_type(self):
        """Test workload type determination."""
        # Test production workload
        resource = {
            'name': 'prod-web-server',
            'tags': {'Environment': 'production'}
        }

        usage_patterns = {
            'avg_cpu_utilization': 70,
            'cpu_variance': 0.1
        }

        workload_type = self.predictor._determine_workload_type(resource, usage_patterns)

        self.assertEqual(workload_type, 'production')

    def test_calculate_base_impact(self):
        """Test base performance impact calculation."""
        optimization = {
            'type': 'rightsizing',
            'description': 'Downsize from t3.large to t3.medium'
        }

        impact = self.predictor._calculate_base_impact(optimization, 'production')

        self.assertIsInstance(impact, float)
        self.assertLess(impact, 0)  # Negative impact for downsizing

    def test_predict_impact_complete(self):
        """Test complete performance impact prediction."""
        resource = {
            'resource_type': 'ec2',
            'name': 'web-server',
            'tags': {'Environment': 'production'}
        }

        optimization = {
            'type': 'rightsizing',
            'description': 'Downsize instance'
        }

        usage_patterns = {
            'avg_cpu_utilization': 30,
            'cpu_variance': 0.2
        }

        result = self.predictor.predict_impact(resource, optimization, usage_patterns)

        # Check required fields
        required_fields = [
            'predicted_performance_impact', 'confidence_level',
            'workload_type', 'recommendations', 'monitoring_suggestions'
        ]

        for field in required_fields:
            self.assertIn(field, result)

        # Check impact is a number
        self.assertIsInstance(result['predicted_performance_impact'], float)

class TestIntegration(unittest.TestCase):
    """Integration tests for ML components working together."""

    def setUp(self):
        self.analyzer = UsagePatternAnalyzer()
        self.assessor = RiskAssessor()
        self.recommender = OptimizationRecommender()
        self.predictor = PerformancePredictor()

    def test_ml_pipeline_integration(self):
        """Test the complete ML pipeline integration."""
        # Sample resource
        resource = {
            'id': 'integration-test-1',
            'name': 'test-web-server',
            'resource_type': 'ec2',
            'instance_type': 't3.large',
            'provider': 'aws',
            'tags': {'Environment': 'production', 'Team': 'engineering'}
        }

        # Sample usage data
        usage_data = [
            {
                'timestamp': f'2024-01-{day:02d}T10:00:00',
                'cpu_utilization': 25,  # Underutilized
                'memory_utilization': 30,
                'network_in': 100,
                'network_out': 80
            }
            for day in range(1, 31)
        ]

        # 1. Analyze usage patterns
        training_result = self.analyzer.train_model(usage_data)
        self.assertIn('status', training_result)

        # 2. Generate recommendations
        usage_patterns = {'integration-test-1': {'avg_cpu_utilization': 25}}
        cost_data = [{
            'resource_id': 'integration-test-1',
            'cost': 30.0,
                            'date': datetime.now(UTC).isoformat()
        }]

        recommendations = self.recommender.generate_recommendations(
            [resource], usage_patterns, cost_data
        )

        self.assertIsInstance(recommendations, list)

        if recommendations:
            rec = recommendations[0]

            # 3. Assess risk
            risk_assessment = self.assessor.assess_risk(resource, rec)
            self.assertIn('overall_risk_score', risk_assessment)

            # 4. Predict performance impact
            performance_prediction = self.predictor.predict_impact(
                resource, rec, usage_patterns['integration-test-1']
            )
            self.assertIn('predicted_performance_impact', performance_prediction)

if __name__ == '__main__':
    # Load test data if available
    try:
        import pandas as pd
        print("Running ML component tests...")
        unittest.main(verbosity=2)
    except ImportError:
        print("Warning: pandas not available, some tests may be skipped")
        unittest.main(verbosity=2)
