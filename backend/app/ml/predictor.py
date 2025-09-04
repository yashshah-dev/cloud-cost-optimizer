from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PerformancePredictor:
    """
    Predicts performance impact of optimization recommendations.
    Uses historical data and resource characteristics to estimate outcomes.
    """

    def __init__(self):
        # Performance impact factors
        self.performance_factors = {
            'cpu_bound': {
                'rightsizing_down': -0.3,  # 30% performance decrease
                'rightsizing_up': 0.2,     # 20% performance increase
                'reserved_instance': 0.0,  # No change
                'spot_instance': 0.0       # No change (assuming same instance type)
            },
            'memory_bound': {
                'rightsizing_down': -0.4,  # 40% performance decrease
                'rightsizing_up': 0.3,     # 30% performance increase
                'reserved_instance': 0.0,
                'spot_instance': 0.0
            },
            'io_bound': {
                'rightsizing_down': -0.2,  # 20% performance decrease
                'rightsizing_up': 0.1,     # 10% performance increase
                'reserved_instance': 0.0,
                'spot_instance': 0.0
            }
        }

        # Risk multipliers based on workload characteristics
        self.risk_multipliers = {
            'production': 1.5,
            'development': 0.7,
            'testing': 0.5,
            'batch_processing': 0.8,
            'real_time': 2.0,
            'user_facing': 1.8
        }

    def predict_impact(self, resource: Dict[str, Any],
                      optimization: Dict[str, Any],
                      usage_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict performance impact of an optimization.

        Args:
            resource: Resource information
            optimization: Optimization recommendation
            usage_patterns: Historical usage patterns

        Returns:
            Performance impact prediction with confidence
        """
        try:
            # Determine workload type
            workload_type = self._determine_workload_type(resource, usage_patterns)

            # Calculate base performance impact
            base_impact = self._calculate_base_impact(optimization, workload_type)

            # Apply risk adjustments
            risk_adjusted_impact = self._apply_risk_adjustments(
                base_impact, resource, optimization
            )

            # Calculate confidence level
            confidence = self._calculate_confidence(
                resource, optimization, usage_patterns
            )

            # Generate recommendations
            recommendations = self._generate_performance_recommendations(
                risk_adjusted_impact, confidence, workload_type
            )

            return {
                "predicted_performance_impact": risk_adjusted_impact,
                "confidence_level": confidence.value,
                "confidence_score": self._confidence_to_score(confidence),
                "workload_type": workload_type,
                "impact_breakdown": self._create_impact_breakdown(
                    base_impact, risk_adjusted_impact
                ),
                "recommendations": recommendations,
                "monitoring_suggestions": self._generate_monitoring_suggestions(
                    optimization, risk_adjusted_impact
                ),
                "rollback_triggers": self._generate_rollback_triggers(
                    risk_adjusted_impact
                ),
                "prediction_timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting performance impact: {e}")
            return {
                "predicted_performance_impact": 0.0,
                "confidence_level": ConfidenceLevel.LOW.value,
                "confidence_score": 0.3,
                "error": str(e),
                "prediction_timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _determine_workload_type(self, resource: Dict[str, Any],
                               usage_patterns: Dict[str, Any]) -> str:
        """Determine the workload type based on resource and usage patterns."""
        try:
            # Check tags for workload type
            tags = resource.get('tags', {})
            for tag_key, tag_value in tags.items():
                tag_key_lower = str(tag_key).lower()
                tag_value_lower = str(tag_value).lower()

                if tag_key_lower in ['workload', 'workload-type', 'environment']:
                    if tag_value_lower in self.risk_multipliers:
                        return tag_value_lower

            # Infer from usage patterns
            avg_cpu = usage_patterns.get('avg_cpu_utilization', 0)
            cpu_variance = usage_patterns.get('cpu_variance', 0)
            peak_cpu = usage_patterns.get('peak_cpu_utilization', 0)

            # High variance suggests batch processing
            if cpu_variance > 0.5:
                return 'batch_processing'

            # Consistently high CPU suggests compute-intensive
            if avg_cpu > 70:
                return 'compute_intensive'

            # Check resource name for clues
            name = resource.get('name', '').lower()
            if any(keyword in name for keyword in ['web', 'api', 'app']):
                return 'user_facing'
            elif any(keyword in name for keyword in ['batch', 'job', 'worker']):
                return 'batch_processing'
            elif 'prod' in name:
                return 'production'

            return 'general'

        except Exception as e:
            logger.error(f"Error determining workload type: {e}")
            return 'general'

    def _calculate_base_impact(self, optimization: Dict[str, Any],
                             workload_type: str) -> float:
        """Calculate base performance impact for the optimization type."""
        try:
            opt_type = optimization.get('type', '').lower()

            # Default impact
            base_impact = 0.0

            # Rightsizing impacts
            if 'rightsizing' in opt_type:
                if 'down' in str(optimization.get('description', '')).lower():
                    # Rightsizing down - negative impact
                    if workload_type in ['user_facing', 'real_time']:
                        base_impact = -0.25  # 25% performance decrease
                    else:
                        base_impact = -0.15  # 15% performance decrease
                else:
                    # Rightsizing up - positive impact
                    base_impact = 0.1  # 10% performance increase

            # Reserved instances - generally no performance impact
            elif 'reserved' in opt_type:
                base_impact = 0.0

            # Spot instances - potential interruption impact
            elif 'spot' in opt_type:
                base_impact = -0.05  # 5% potential impact due to interruptions

            # Storage optimization - minimal impact
            elif 'storage' in opt_type:
                base_impact = -0.02  # 2% potential impact

            return base_impact

        except Exception as e:
            logger.error(f"Error calculating base impact: {e}")
            return 0.0

    def _apply_risk_adjustments(self, base_impact: float,
                              resource: Dict[str, Any],
                              optimization: Dict[str, Any]) -> float:
        """Apply risk-based adjustments to the base impact."""
        try:
            adjusted_impact = base_impact

            # Apply workload type multiplier
            workload_type = self._determine_workload_type(resource, {})
            if workload_type in self.risk_multipliers:
                multiplier = self.risk_multipliers[workload_type]
                adjusted_impact *= multiplier

            # Adjust for resource criticality
            tags = resource.get('tags', {})
            for tag_key, tag_value in tags.items():
                if (str(tag_key).lower() in ['criticality', 'importance'] and
                    str(tag_value).lower() in ['high', 'critical']):
                    adjusted_impact *= 1.3  # Increase impact magnitude for critical resources

            # Adjust for optimization complexity
            complexity = optimization.get('implementation_complexity', 'medium')
            if complexity == 'high':
                adjusted_impact *= 1.2
            elif complexity == 'low':
                adjusted_impact *= 0.9

            return adjusted_impact

        except Exception as e:
            logger.error(f"Error applying risk adjustments: {e}")
            return base_impact

    def _calculate_confidence(self, resource: Dict[str, Any],
                           optimization: Dict[str, Any],
                           usage_patterns: Dict[str, Any]) -> ConfidenceLevel:
        """Calculate confidence level in the performance prediction."""
        try:
            confidence_score = 0.5  # Base confidence

            # Increase confidence based on data availability
            if usage_patterns.get('data_points', 0) > 100:
                confidence_score += 0.2

            # Increase confidence for simpler optimizations
            complexity = optimization.get('implementation_complexity', 'medium')
            if complexity == 'low':
                confidence_score += 0.15
            elif complexity == 'high':
                confidence_score -= 0.1

            # Increase confidence for well-known resource types
            resource_type = resource.get('resource_type', '').lower()
            if any(known_type in resource_type for known_type in
                   ['ec2', 'rds', 'lambda', 's3', 'elb']):
                confidence_score += 0.1

            # Determine confidence level
            if confidence_score >= 0.8:
                return ConfidenceLevel.HIGH
            elif confidence_score >= 0.6:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return ConfidenceLevel.LOW

    def _confidence_to_score(self, confidence: ConfidenceLevel) -> float:
        """Convert confidence level to numerical score."""
        mapping = {
            ConfidenceLevel.LOW: 0.4,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.HIGH: 0.9
        }
        return mapping.get(confidence, 0.5)

    def _create_impact_breakdown(self, base_impact: float,
                               adjusted_impact: float) -> Dict[str, Any]:
        """Create detailed breakdown of performance impact factors."""
        return {
            "base_impact": base_impact,
            "risk_adjustments": adjusted_impact - base_impact,
            "final_impact": adjusted_impact,
            "impact_percentage": adjusted_impact * 100,
            "impact_direction": "positive" if adjusted_impact > 0 else "negative" if adjusted_impact < 0 else "neutral"
        }

    def _generate_performance_recommendations(self, impact: float,
                                            confidence: ConfidenceLevel,
                                            workload_type: str) -> List[str]:
        """Generate performance-related recommendations."""
        recommendations = []

        if confidence == ConfidenceLevel.LOW:
            recommendations.append("Monitor performance closely after implementation")
            recommendations.append("Have rollback plan ready")

        if abs(impact) > 0.2:  # Significant impact
            recommendations.append("Consider gradual rollout or canary deployment")
            recommendations.append("Set up detailed performance monitoring")

        if impact < -0.1:  # Negative impact expected
            recommendations.append("Test thoroughly in staging environment first")
            recommendations.append("Prepare performance baseline measurements")

        if workload_type in ['user_facing', 'real_time']:
            recommendations.append("Schedule during low-traffic periods")
            recommendations.append("Have additional capacity ready for rollback")

        return recommendations

    def _generate_monitoring_suggestions(self, optimization: Dict[str, Any],
                                       impact: float) -> List[str]:
        """Generate monitoring suggestions based on optimization type."""
        suggestions = []

        opt_type = optimization.get('type', '').lower()

        # Common monitoring
        suggestions.extend([
            "Monitor CPU utilization trends",
            "Track response times and latency",
            "Monitor error rates and failed requests"
        ])

        # Type-specific monitoring
        if 'rightsizing' in opt_type:
            suggestions.extend([
                "Monitor memory pressure",
                "Track I/O wait times",
                "Monitor application performance metrics"
            ])

        elif 'storage' in opt_type:
            suggestions.extend([
                "Monitor disk I/O operations",
                "Track storage latency",
                "Monitor cache hit rates"
            ])

        elif 'spot' in opt_type:
            suggestions.extend([
                "Monitor instance interruptions",
                "Track spot instance pricing",
                "Monitor failover events"
            ])

        # Impact-based monitoring
        if abs(impact) > 0.15:
            suggestions.append("Set up alerts for performance degradation")
            suggestions.append("Monitor business KPIs closely")

        return suggestions

    def _generate_rollback_triggers(self, impact: float) -> List[str]:
        """Generate rollback trigger conditions."""
        triggers = []

        # Common triggers
        triggers.extend([
            "Error rate increases by >25%",
            "Response time increases by >50%",
            "CPU utilization consistently >90%"
        ])

        # Impact-specific triggers
        if abs(impact) > 0.2:
            triggers.extend([
                "Performance degradation detected",
                "Business metric impact observed",
                "User complaints reported"
            ])

        return triggers

    def validate_prediction_accuracy(self, actual_performance: Dict[str, Any],
                                   predicted_impact: float) -> Dict[str, Any]:
        """
        Validate prediction accuracy against actual performance data.

        Args:
            actual_performance: Actual performance metrics after optimization
            predicted_impact: Predicted performance impact

        Returns:
            Validation results and accuracy metrics
        """
        try:
            # This would be implemented with actual performance comparison logic
            # For now, return a placeholder structure

            return {
                "prediction_accuracy": 0.0,  # Would calculate actual vs predicted
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "recommendations": [
                    "Update model with new performance data",
                    "Refine prediction algorithms based on results"
                ]
            }

        except Exception as e:
            logger.error(f"Error validating prediction: {e}")
            return {"error": str(e)}
