"""
AWS Provider wrapper for the cost optimization system.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import date
from .aws_client import AWSClient
from .base import CloudProvider, ResourceType, CloudResourceDTO, CostEntryDTO

class AWSProvider:
    """AWS provider implementation for cost optimization"""

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize AWS client with credentials from environment"""
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if access_key and secret_key:
            self.client = AWSClient(access_key, secret_key, region)

    async def get_resources(self, account_config: Dict[str, Any]) -> List[CloudResourceDTO]:
        """Get AWS resources for optimization"""
        if not self.client:
            return []

        try:
            # Authenticate if not already done
            if not self.client.is_authenticated():
                await self.client.authenticate()

            # Get resources
            resources = await self.client.get_resources()
            return resources
        except Exception as e:
            print(f"Error getting AWS resources: {e}")
            return []

    async def optimize_cost(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource for cost optimization opportunities"""
        if not self.client:
            return {"recommendations": []}

        try:
            # Get usage metrics for the resource
            resource_id = resource_data.get("resource_id", "")
            start_date = date.today().replace(day=1)  # Start of current month
            end_date = date.today()

            metrics = await self.client.get_usage_metrics(resource_id, start_date, end_date)

            # Simple optimization logic based on metrics
            recommendations = []

            # Check CPU utilization
            if "cpu_utilization" in metrics:
                cpu_data = metrics["cpu_utilization"]
                if cpu_data:
                    avg_cpu = sum(point.get("average", 0) for point in cpu_data) / len(cpu_data)

                    if avg_cpu < 20:
                        recommendations.append({
                            "type": "rightsizing",
                            "description": f"Low CPU utilization ({avg_cpu:.1f}%). Consider downsizing instance type.",
                            "potential_savings": "20-40%",
                            "priority": "high"
                        })
                    elif avg_cpu > 80:
                        recommendations.append({
                            "type": "upsizing",
                            "description": f"High CPU utilization ({avg_cpu:.1f}%). Consider upgrading instance type.",
                            "potential_savings": "N/A - performance improvement",
                            "priority": "medium"
                        })

            return {
                "resource_id": resource_id,
                "recommendations": recommendations,
                "analysis_date": str(date.today())
            }

        except Exception as e:
            print(f"Error optimizing AWS resource: {e}")
            return {"recommendations": []}

    async def generate_cost_report(self, date_range: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost report for AWS resources"""
        if not self.client:
            return {"total_cost": 0, "resources": []}

        try:
            start_date = date.fromisoformat(date_range.get("start_date", str(date.today().replace(day=1))))
            end_date = date.fromisoformat(date_range.get("end_date", str(date.today())))

            cost_data = await self.client.get_cost_data(start_date, end_date)

            total_cost = sum(entry.cost for entry in cost_data)

            return {
                "provider": "aws",
                "total_cost": total_cost,
                "currency": "USD",
                "date_range": date_range,
                "resources": len(set(entry.resource_id for entry in cost_data)),
                "services": list(set(entry.service_name for entry in cost_data))
            }

        except Exception as e:
            print(f"Error generating AWS cost report: {e}")
            return {"total_cost": 0, "resources": [], "error": str(e)}
