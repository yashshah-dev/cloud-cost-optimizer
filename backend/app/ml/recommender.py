from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime, timedelta, timezone
import math

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCE = "reserved_instance"
    SPOT_INSTANCE = "spot_instance"
    STORAGE_OPTIMIZATION = "storage_optimization"
    AUTO_SCALING = "auto_scaling"
    UNUSED_RESOURCE = "unused_resource"

class OptimizationRecommender:
    """
    Generates optimization recommendations based on usage patterns and cost analysis.
    Prioritizes recommendations by potential savings and risk level.
    """

    def __init__(self):
        self.cost_savings_weights = {
            'cpu_overprovisioned': 0.4,
            'memory_overprovisioned': 0.3,
            'storage_underutilized': 0.2,
            'idle_time': 0.1
        }

        # Instance type mappings (simplified)
        self.instance_families = {
            't2': 'general_purpose',
            't3': 'general_purpose',
            'm5': 'general_purpose',
            'm6': 'general_purpose',
            'c5': 'compute_optimized',
            'c6': 'compute_optimized',
            'r5': 'memory_optimized',
            'r6': 'memory_optimized'
        }

    def generate_recommendations(self, resources: List[Dict[str, Any]],
                               usage_patterns: Dict[str, Any],
                               cost_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations for a set of resources.

        Args:
            resources: List of cloud resources
            usage_patterns: Usage pattern analysis results
            cost_data: Historical cost data

        Returns:
            List of prioritized optimization recommendations
        """
        recommendations = []

        try:
            for resource in resources:
                resource_recs = self._analyze_resource(resource, usage_patterns, cost_data)
                recommendations.extend(resource_recs)

            # Sort by potential savings (highest first)
            recommendations.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)

            # Add priority ranking
            for i, rec in enumerate(recommendations):
                rec['priority_rank'] = i + 1
                rec['priority_level'] = self._calculate_priority_level(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def _analyze_resource(self, resource: Dict[str, Any],
                         usage_patterns: Dict[str, Any],
                         cost_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a single resource for optimization opportunities."""
        recommendations = []
        resource_id = resource.get('id')

        try:
            # Get usage pattern for this resource
            resource_usage = usage_patterns.get(str(resource_id), {})

            # Rightsizing analysis
            rightsizing_rec = self._analyze_rightsizing(resource, resource_usage)
            if rightsizing_rec:
                recommendations.append(rightsizing_rec)

            # Reserved instance analysis
            reserved_rec = self._analyze_reserved_instance(resource, cost_data)
            if reserved_rec:
                recommendations.append(reserved_rec)

            # Spot instance analysis
            spot_rec = self._analyze_spot_instance(resource, resource_usage)
            if spot_rec:
                recommendations.append(spot_rec)

            # Storage optimization
            storage_rec = self._analyze_storage_optimization(resource, resource_usage)
            if storage_rec:
                recommendations.append(storage_rec)

            # Unused resource detection
            unused_rec = self._analyze_unused_resource(resource, resource_usage)
            if unused_rec:
                recommendations.append(unused_rec)

        except Exception as e:
            logger.error(f"Error analyzing resource {resource_id}: {e}")

        return recommendations

    def _analyze_rightsizing(self, resource: Dict[str, Any],
                           usage_patterns: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze if resource is over/under-provisioned."""
        try:
            current_instance = resource.get('instance_type', '')
            avg_cpu = usage_patterns.get('avg_cpu_utilization', 0)
            avg_memory = usage_patterns.get('avg_memory_utilization', 0)
            peak_cpu = usage_patterns.get('peak_cpu_utilization', 0)

            # Simple rightsizing logic
            recommended_instance = current_instance
            savings_potential = 0
            reason = ""

            # CPU-based rightsizing
            if avg_cpu < 20 and peak_cpu < 40:
                # Significantly underutilized - downsize
                recommended_instance = self._get_smaller_instance(current_instance)
                savings_potential = self._calculate_instance_savings(current_instance, recommended_instance)
                reason = ".1f"

            elif avg_cpu > 80 and peak_cpu > 90:
                # Consistently high utilization - upscale
                recommended_instance = self._get_larger_instance(current_instance)
                savings_potential = 0  # Actually cost increase, but for performance
                reason = ".1f"

            elif 40 <= avg_cpu <= 70:
                # Good utilization - no change needed
                return None

            if recommended_instance != current_instance and savings_potential > 10:
                return {
                    "id": f"rightsizing_{resource['id']}_{datetime.now(timezone.utc).timestamp()}",
                    "resource_id": resource['id'],
                    "type": OptimizationType.RIGHTSIZING.value,
                    "title": "Rightsize Instance",
                    "description": reason,
                    "current_instance": current_instance,
                    "recommended_instance": recommended_instance,
                    "potential_savings": savings_potential,
                    "confidence_score": 0.8,
                    "implementation_complexity": "medium",
                    "estimated_effort_hours": 2,
                    "requires_downtime": True,
                    "rollback_complexity": "low",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error in rightsizing analysis: {e}")

        return None

    def _analyze_reserved_instance(self, resource: Dict[str, Any],
                                 cost_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze potential for reserved instance purchase."""
        try:
            # Get recent cost data for this resource
            resource_costs = [c for c in cost_data if c.get('resource_id') == resource.get('id')]

            if len(resource_costs) < 30:  # Need at least 30 days of data
                return None

            # Calculate average daily cost
            total_cost = sum(c.get('cost', 0) for c in resource_costs)
            avg_daily_cost = total_cost / len(resource_costs)

            # Reserved instance discount (approximate 30-50% savings)
            discount_rate = 0.4  # 40% savings
            monthly_savings = avg_daily_cost * 30 * discount_rate

            # Only recommend if savings > $50/month
            if monthly_savings > 50:
                return {
                    "id": f"reserved_{resource['id']}_{datetime.now(timezone.utc).timestamp()}",
                    "resource_id": resource['id'],
                    "type": OptimizationType.RESERVED_INSTANCE.value,
                    "title": "Purchase Reserved Instance",
                    "description": f"This {resource.get('resource_type', 'resource')} shows consistent usage patterns. Purchasing a reserved instance would provide ${monthly_savings:.2f} in monthly savings.",
                    "current_cost_monthly": avg_daily_cost * 30,
                    "reserved_cost_monthly": avg_daily_cost * 30 * (1 - discount_rate),
                    "potential_savings": monthly_savings,
                    "confidence_score": 0.9,
                    "implementation_complexity": "low",
                    "estimated_effort_hours": 1,
                    "requires_downtime": False,
                    "rollback_complexity": "high",  # Hard to cancel reserved instances
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error in reserved instance analysis: {e}")

        return None

    def _analyze_spot_instance(self, resource: Dict[str, Any],
                             usage_patterns: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze potential for spot instance usage."""
        try:
            # Spot instances are good for fault-tolerant workloads
            avg_cpu = usage_patterns.get('avg_cpu_utilization', 0)
            instance_type = resource.get('instance_type', '')

            # Only recommend for certain workloads
            if avg_cpu > 70:  # High utilization - not suitable for spot
                return None

            # Calculate potential savings (spot instances can be 50-90% cheaper)
            spot_discount = 0.7  # 70% savings on average
            monthly_cost = resource.get('monthly_cost', 0)
            monthly_savings = monthly_cost * spot_discount

            if monthly_savings > 20:  # Minimum savings threshold
                return {
                    "id": f"spot_{resource['id']}_{datetime.now(timezone.utc).timestamp()}",
                    "resource_id": resource['id'],
                    "type": OptimizationType.SPOT_INSTANCE.value,
                    "title": "Use Spot Instances",
                    "description": f"This {resource.get('resource_type', 'resource')} can be converted to a spot instance, providing ${monthly_savings:.2f} in monthly savings.",
                    "current_cost_monthly": monthly_cost,
                    "spot_cost_monthly": monthly_cost * (1 - spot_discount),
                    "potential_savings": monthly_savings,
                    "confidence_score": 0.6,  # Lower confidence due to spot instance interruptions
                    "implementation_complexity": "medium",
                    "estimated_effort_hours": 4,
                    "requires_downtime": True,
                    "rollback_complexity": "medium",
                    "risk_factors": ["Spot instance interruptions", "Need fault-tolerant architecture"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error in spot instance analysis: {e}")

        return None

    def _analyze_storage_optimization(self, resource: Dict[str, Any],
                                    usage_patterns: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze storage optimization opportunities."""
        try:
            # Check if this is a storage resource
            if 'storage' not in resource.get('resource_type', '').lower():
                return None

            storage_used = usage_patterns.get('storage_used_gb', 0)
            storage_allocated = usage_patterns.get('storage_allocated_gb', 0)

            if storage_allocated == 0:
                return None

            utilization_rate = storage_used / storage_allocated

            if utilization_rate < 0.3:  # Less than 30% utilization
                # Calculate potential savings
                storage_cost_per_gb = resource.get('cost_per_gb', 0.1)  # Default $0.10/GB/month
                overprovisioned_gb = storage_allocated - storage_used
                monthly_savings = overprovisioned_gb * storage_cost_per_gb

                if monthly_savings > 10:  # Minimum savings threshold
                    return {
                        "id": f"storage_{resource['id']}_{datetime.now(timezone.utc).timestamp()}",
                        "resource_id": resource['id'],
                        "type": OptimizationType.STORAGE_OPTIMIZATION.value,
                        "title": "Optimize Storage Allocation",
                        "description": f"This storage resource is only {utilization_rate:.1%} utilized. Reducing allocation could save ${monthly_savings:.1f} monthly.",
                        "current_storage_gb": storage_allocated,
                        "recommended_storage_gb": storage_used * 1.2,  # 20% buffer
                        "potential_savings": monthly_savings,
                        "confidence_score": 0.85,
                        "implementation_complexity": "low",
                        "estimated_effort_hours": 1,
                    "requires_downtime": False,
                    "rollback_complexity": "low",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error in storage optimization analysis: {e}")

        return None

    def _analyze_unused_resource(self, resource: Dict[str, Any],
                               usage_patterns: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect potentially unused resources."""
        try:
            avg_cpu = usage_patterns.get('avg_cpu_utilization', 0)
            avg_network = usage_patterns.get('avg_network_utilization', 0)
            last_activity = usage_patterns.get('last_activity_days', 0)

            # Criteria for unused resource
            is_unused = (
                avg_cpu < 5 and  # Very low CPU usage
                avg_network < 10 and  # Very low network activity
                last_activity > 7  # No activity for more than a week
            )

            if is_unused:
                monthly_cost = resource.get('monthly_cost', 0)
                return {
                    "id": f"unused_{resource['id']}_{datetime.now(timezone.utc).timestamp()}",
                    "resource_id": resource['id'],
                    "type": OptimizationType.UNUSED_RESOURCE.value,
                    "title": "Terminate Unused Resource",
                    "description": f"This resource shows very low activity (CPU: {avg_cpu:.1f}%, Network: {avg_network:.1f}%, Last activity: {last_activity} days ago). Terminating it could save ${monthly_cost:.1f} monthly.",
                    "potential_savings": monthly_cost,
                    "confidence_score": 0.7,
                    "implementation_complexity": "low",
                    "estimated_effort_hours": 0.5,
                    "requires_downtime": True,
                    "rollback_complexity": "medium",  # Resource termination
                    "risk_factors": ["Data loss if resource contains important data"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            logger.error(f"Error in unused resource analysis: {e}")

        return None

    def _get_smaller_instance(self, current_instance: str) -> str:
        """Get a smaller instance type recommendation."""
        # Simplified instance sizing logic
        instance_mappings = {
            't3.medium': 't3.small',
            't3.large': 't3.medium',
            'm5.large': 'm5.medium',
            'm5.xlarge': 'm5.large',
            'c5.large': 'c5.medium',
            'r5.large': 'r5.medium'
        }
        return instance_mappings.get(current_instance, current_instance)

    def _get_larger_instance(self, current_instance: str) -> str:
        """Get a larger instance type recommendation."""
        instance_mappings = {
            't3.small': 't3.medium',
            't3.medium': 't3.large',
            'm5.medium': 'm5.large',
            'm5.large': 'm5.xlarge',
            'c5.medium': 'c5.large',
            'r5.medium': 'r5.large'
        }
        return instance_mappings.get(current_instance, current_instance)

    def _calculate_instance_savings(self, current: str, recommended: str) -> float:
        """Calculate potential savings from instance type change."""
        # Simplified cost calculation (in real implementation, use actual pricing)
        instance_costs = {
            't3.small': 10, 't3.medium': 20, 't3.large': 40,
            'm5.medium': 30, 'm5.large': 60, 'm5.xlarge': 120,
            'c5.medium': 40, 'c5.large': 80,
            'r5.medium': 50, 'r5.large': 100
        }

        current_cost = instance_costs.get(current, 50)
        recommended_cost = instance_costs.get(recommended, 50)

        return max(0, current_cost - recommended_cost)

    def _calculate_priority_level(self, recommendation: Dict[str, Any]) -> str:
        """Calculate priority level for a recommendation."""
        savings = recommendation.get('potential_savings', 0)
        confidence = recommendation.get('confidence_score', 0)
        complexity = recommendation.get('implementation_complexity', 'medium')

        # Priority scoring
        priority_score = savings * confidence

        # Adjust for complexity
        if complexity == 'low':
            priority_score *= 1.2
        elif complexity == 'high':
            priority_score *= 0.8

        if priority_score > 500:
            return "critical"
        elif priority_score > 200:
            return "high"
        elif priority_score > 50:
            return "medium"
        else:
            return "low"
