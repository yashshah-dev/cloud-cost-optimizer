from typing import Dict, Any, List, Optional
from enum import Enum
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessor:
    """
    Assesses business and technical risks for optimization recommendations.
    Evaluates resource criticality, business impact, and rollback complexity.
    """

    def __init__(self):
        # Risk scoring weights
        self.weights = {
            'resource_criticality': 0.3,
            'business_impact': 0.3,
            'rollback_complexity': 0.2,
            'data_sensitivity': 0.1,
            'uptime_requirements': 0.1
        }

        # Critical resource types
        self.critical_resource_types = {
            'database', 'load_balancer', 'api_gateway', 'cache',
            'message_queue', 'storage_gateway'
        }

        # High business impact tags
        self.high_impact_tags = {
            'production', 'critical', 'revenue-generating',
            'customer-facing', 'compliance-required'
        }

    def assess_risk(self, resource: Dict[str, Any], optimization: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall risk for a resource optimization.

        Args:
            resource: Resource information
            optimization: Optimization recommendation details

        Returns:
            Risk assessment with score and breakdown
        """
        try:
            # Individual risk components
            resource_risk = self._assess_resource_criticality(resource)
            business_risk = self._assess_business_impact(resource)
            rollback_risk = self._assess_rollback_complexity(optimization)
            data_risk = self._assess_data_sensitivity(resource)
            uptime_risk = self._assess_uptime_requirements(resource)

            # Calculate weighted risk score
            risk_score = (
                resource_risk['score'] * self.weights['resource_criticality'] +
                business_risk['score'] * self.weights['business_impact'] +
                rollback_risk['score'] * self.weights['rollback_complexity'] +
                data_risk['score'] * self.weights['data_sensitivity'] +
                uptime_risk['score'] * self.weights['uptime_requirements']
            )

            # Determine overall risk level
            risk_level = self._calculate_risk_level(risk_score)

            # Generate recommendations
            recommendations = self._generate_risk_recommendations(
                risk_level, resource_risk, business_risk, rollback_risk
            )

            return {
                "overall_risk_score": risk_score,
                "risk_level": risk_level.value,
                "assessment_breakdown": {
                    "resource_criticality": resource_risk,
                    "business_impact": business_risk,
                    "rollback_complexity": rollback_risk,
                    "data_sensitivity": data_risk,
                    "uptime_requirements": uptime_risk
                },
                "recommendations": recommendations,
                "requires_approval": risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
                "auto_approval_eligible": risk_level == RiskLevel.LOW,
                "assessment_timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return {
                "overall_risk_score": 0.5,
                "risk_level": RiskLevel.MEDIUM.value,
                "error": str(e),
                "assessment_timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _assess_resource_criticality(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how critical the resource is to system operations."""
        resource_type = resource.get('resource_type', '').lower()
        name = resource.get('name', '').lower()
        tags = resource.get('tags', {})

        score = 0.0
        factors = []

        # Check resource type
        if any(critical_type in resource_type for critical_type in self.critical_resource_types):
            score += 0.4
            factors.append("Critical resource type")

        # Check resource name for critical indicators
        critical_indicators = ['prod', 'production', 'critical', 'main', 'primary']
        if any(indicator in name for indicator in critical_indicators):
            score += 0.3
            factors.append("Critical naming pattern")

        # Check tags
        tag_keys = [k.lower() for k in tags.keys()]
        tag_values = [str(v).lower() for v in tags.values()]

        for tag_key, tag_value in tags.items():
            if (tag_key.lower() in ['environment', 'tier', 'importance'] and
                str(tag_value).lower() in ['production', 'prod', 'critical', 'high']):
                score += 0.3
                factors.append(f"Critical tag: {tag_key}={tag_value}")
                break

        return {
            "score": min(score, 1.0),
            "factors": factors,
            "description": f"Resource criticality assessment: {', '.join(factors) if factors else 'Standard resource'}"
        }

    def _assess_business_impact(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential business impact of resource optimization."""
        tags = resource.get('tags', {})
        name = resource.get('name', '').lower()

        score = 0.0
        factors = []

        # Check for high-impact tags
        for tag_key, tag_value in tags.items():
            tag_key_lower = str(tag_key).lower()
            tag_value_lower = str(tag_value).lower()

            if (tag_key_lower in ['business-unit', 'department', 'owner'] and
                tag_value_lower in ['finance', 'sales', 'customer-service', 'operations']):
                score += 0.3
                factors.append(f"Business-critical tag: {tag_key}={tag_value}")

            if tag_value_lower in self.high_impact_tags:
                score += 0.4
                factors.append(f"High impact tag: {tag_value}")

        # Check resource naming for business indicators
        business_indicators = ['web', 'api', 'app', 'service', 'customer']
        if any(indicator in name for indicator in business_indicators):
            score += 0.2
            factors.append("Customer-facing resource")

        # Check for compliance requirements
        compliance_tags = ['pci', 'hipaa', 'gdpr', 'sox', 'compliance']
        for tag_key, tag_value in tags.items():
            if any(compliance in str(tag_value).lower() for compliance in compliance_tags):
                score += 0.3
                factors.append(f"Compliance requirement: {tag_value}")

        return {
            "score": min(score, 1.0),
            "factors": factors,
            "description": f"Business impact assessment: {', '.join(factors) if factors else 'Standard business impact'}"
        }

    def _assess_rollback_complexity(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Assess complexity of rolling back the optimization."""
        optimization_type = optimization.get('type', '').lower()

        score = 0.0
        factors = []

        # Rightsizing changes are generally easy to rollback
        if 'rightsizing' in optimization_type:
            score += 0.2
            factors.append("Rightsizing - relatively simple rollback")

        # Instance type changes may require migration
        elif 'instance' in optimization_type or 'resize' in optimization_type:
            score += 0.4
            factors.append("Instance type change - may require migration")

        # Reserved instance purchases are hard to rollback
        elif 'reserved' in optimization_type:
            score += 0.7
            factors.append("Reserved instance purchase - complex rollback")

        # Spot instance changes can be risky
        elif 'spot' in optimization_type:
            score += 0.6
            factors.append("Spot instance change - potential service interruption")

        # Storage changes can be complex
        elif 'storage' in optimization_type:
            score += 0.5
            factors.append("Storage optimization - data migration complexity")

        # Default medium complexity
        else:
            score += 0.4
            factors.append("Standard optimization complexity")

        # Check for data migration requirements
        if optimization.get('requires_data_migration', False):
            score += 0.3
            factors.append("Requires data migration")

        return {
            "score": min(score, 1.0),
            "factors": factors,
            "description": f"Rollback complexity: {', '.join(factors)}"
        }

    def _assess_data_sensitivity(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data sensitivity and security requirements."""
        tags = resource.get('tags', {})
        resource_type = resource.get('resource_type', '').lower()

        score = 0.0
        factors = []

        # Check for sensitive data tags
        sensitive_tags = ['pii', 'phi', 'sensitive', 'confidential', 'encrypted']
        for tag_key, tag_value in tags.items():
            if any(sensitive in str(tag_value).lower() for sensitive in sensitive_tags):
                score += 0.6
                factors.append(f"Sensitive data: {tag_value}")
                break

        # Database resources often contain sensitive data
        if 'database' in resource_type or 'db' in resource_type:
            score += 0.4
            factors.append("Database resource - potential sensitive data")

        # Storage resources may contain backups
        if 'storage' in resource_type or 'backup' in resource_type:
            score += 0.3
            factors.append("Storage resource - potential sensitive data")

        return {
            "score": min(score, 1.0),
            "factors": factors,
            "description": f"Data sensitivity: {', '.join(factors) if factors else 'Standard data handling'}"
        }

    def _assess_uptime_requirements(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Assess uptime and availability requirements."""
        tags = resource.get('tags', {})
        name = resource.get('name', '').lower()

        score = 0.0
        factors = []

        # Check for SLA tags
        for tag_key, tag_value in tags.items():
            if 'sla' in str(tag_key).lower():
                sla_value = str(tag_value).lower()
                if '99.9' in sla_value or 'high' in sla_value:
                    score += 0.5
                    factors.append(f"High SLA requirement: {tag_value}")
                elif '99' in sla_value:
                    score += 0.3
                    factors.append(f"Standard SLA requirement: {tag_value}")

        # Check for availability zone requirements
        if 'multi-az' in name or 'ha' in name or 'high-availability' in name:
            score += 0.4
            factors.append("High availability requirement indicated")

        # Production resources typically have higher uptime requirements
        if 'prod' in name or 'production' in name:
            score += 0.3
            factors.append("Production environment - high uptime expected")

        return {
            "score": min(score, 1.0),
            "factors": factors,
            "description": f"Uptime requirements: {', '.join(factors) if factors else 'Standard availability'}"
        }

    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Calculate overall risk level from risk score."""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_risk_recommendations(self, risk_level: RiskLevel,
                                     resource_risk: Dict, business_risk: Dict,
                                     rollback_risk: Dict) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Requires senior management approval",
                "Schedule during low-traffic maintenance window",
                "Prepare detailed rollback plan with testing",
                "Monitor closely for 72 hours post-optimization",
                "Have on-call team ready for immediate rollback"
            ])

        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Requires technical lead approval",
                "Schedule during business hours for monitoring",
                "Test rollback procedure before execution",
                "Monitor for 24 hours post-optimization",
                "Document all changes and monitoring results"
            ])

        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Requires peer review and approval",
                "Monitor for 12 hours post-optimization",
                "Document changes and results",
                "Consider gradual rollout if possible"
            ])

        else:  # LOW
            recommendations.extend([
                "Can be auto-approved",
                "Monitor for 4 hours post-optimization",
                "Log changes for audit trail"
            ])

        # Add specific recommendations based on risk factors
        if resource_risk['score'] > 0.5:
            recommendations.append("Consider alternative optimization strategies for critical resources")

        if business_risk['score'] > 0.5:
            recommendations.append("Engage business stakeholders for impact assessment")

        if rollback_risk['score'] > 0.5:
            recommendations.append("Ensure backup and restore procedures are tested")

        return recommendations
