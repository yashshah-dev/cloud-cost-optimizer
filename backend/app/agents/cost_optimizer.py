from typing import Dict, Any, List
import json
import logging
from datetime import datetime

from .base import BaseAgent, BaseTool, AgentContext, AgentMessage

logger = logging.getLogger(__name__)

class CostAnalysisTool(BaseTool):
    """Tool for analyzing cost data"""
    
    @property
    def name(self) -> str:
        return "cost_analysis"
    
    @property
    def description(self) -> str:
        return "Analyze cost data and identify trends, anomalies, and insights"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "time_period": {"type": "string", "description": "Time period for analysis"},
                "providers": {"type": "array", "items": {"type": "string"}},
                "resource_types": {"type": "array", "items": {"type": "string"}},
                "analysis_type": {"type": "string", "enum": ["trend", "anomaly", "comparison"]}
            },
            "required": ["time_period", "analysis_type"]
        }
    
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Any:
        """Execute cost analysis"""
        try:
            # Placeholder implementation - will connect to database in Phase 2
            analysis_type = parameters.get("analysis_type")
            time_period = parameters.get("time_period")
            
            result = {
                "analysis_type": analysis_type,
                "time_period": time_period,
                "insights": [],
                "recommendations": [],
                "status": "placeholder"
            }
            
            if analysis_type == "trend":
                result["insights"] = [
                    "Compute costs increased by 15% over the last month",
                    "Storage costs remained stable",
                    "Network costs show seasonal variation"
                ]
            elif analysis_type == "anomaly":
                result["insights"] = [
                    "Unusual spike in database costs on 2024-01-15",
                    "Weekend compute usage higher than expected"
                ]
            elif analysis_type == "comparison":
                result["insights"] = [
                    "AWS costs 20% higher than GCP for similar workloads",
                    "Reserved instances show 35% savings potential"
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in cost analysis tool: {e}")
            return {"error": str(e), "status": "failed"}

class OptimizationTool(BaseTool):
    """Tool for generating optimization recommendations"""
    
    @property
    def name(self) -> str:
        return "optimization_recommendations"
    
    @property
    def description(self) -> str:
        return "Generate cost optimization recommendations based on usage patterns"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "resource_ids": {"type": "array", "items": {"type": "string"}},
                "optimization_types": {"type": "array", "items": {"type": "string"}},
                "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]},
                "min_savings": {"type": "number", "minimum": 0}
            }
        }
    
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Any:
        """Execute optimization recommendations"""
        try:
            risk_tolerance = parameters.get("risk_tolerance", "medium")
            min_savings = parameters.get("min_savings", 0)
            
            # Placeholder recommendations
            recommendations = [
                {
                    "type": "rightsizing",
                    "title": "Downsize over-provisioned instances",
                    "description": "3 instances can be downsized based on utilization patterns",
                    "potential_savings": 450.00,
                    "risk_level": "low",
                    "confidence": 0.9
                },
                {
                    "type": "reserved_instances",
                    "title": "Purchase Reserved Instances",
                    "description": "Convert 5 on-demand instances to reserved for long-term workloads",
                    "potential_savings": 1200.00,
                    "risk_level": "medium",
                    "confidence": 0.85
                },
                {
                    "type": "storage_optimization",
                    "title": "Optimize storage tiers",
                    "description": "Move infrequently accessed data to cheaper storage tiers",
                    "potential_savings": 300.00,
                    "risk_level": "low",
                    "confidence": 0.8
                }
            ]
            
            # Filter by risk tolerance and minimum savings
            filtered_recommendations = [
                rec for rec in recommendations
                if rec["potential_savings"] >= min_savings
                and self._risk_level_score(rec["risk_level"]) <= self._risk_level_score(risk_tolerance)
            ]
            
            return {
                "recommendations": filtered_recommendations,
                "total_potential_savings": sum(rec["potential_savings"] for rec in filtered_recommendations),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in optimization tool: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _risk_level_score(self, risk_level: str) -> int:
        """Convert risk level to numeric score"""
        scores = {"low": 1, "medium": 2, "high": 3}
        return scores.get(risk_level, 2)

class ResourceDiscoveryTool(BaseTool):
    """Tool for discovering cloud resources"""
    
    @property
    def name(self) -> str:
        return "resource_discovery"
    
    @property
    def description(self) -> str:
        return "Discover and analyze cloud resources across providers"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "providers": {"type": "array", "items": {"type": "string"}},
                "resource_types": {"type": "array", "items": {"type": "string"}},
                "regions": {"type": "array", "items": {"type": "string"}},
                "include_costs": {"type": "boolean", "default": True}
            }
        }
    
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Any:
        """Execute resource discovery"""
        try:
            providers = parameters.get("providers", ["aws"])
            include_costs = parameters.get("include_costs", True)
            
            # Placeholder implementation
            discovered_resources = {
                "total_resources": 42,
                "by_provider": {"aws": 30, "gcp": 8, "azure": 4},
                "by_type": {"compute": 20, "storage": 15, "database": 5, "network": 2},
                "total_monthly_cost": 2450.00 if include_costs else None,
                "last_updated": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            return discovered_resources
            
        except Exception as e:
            logger.error(f"Error in resource discovery tool: {e}")
            return {"error": str(e), "status": "failed"}

class CostOptimizerAgent(BaseAgent):
    """AI agent for cost optimization"""
    
    def __init__(self):
        super().__init__(
            name="Cost Optimizer Agent",
            description="AI agent that provides intelligent cost optimization recommendations"
        )
        
        # Add tools
        self.add_tool(CostAnalysisTool())
        self.add_tool(OptimizationTool())
        self.add_tool(ResourceDiscoveryTool())
    
    async def process_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Process a user query and return response"""
        try:
            # Simple intent detection (will be enhanced with LLM in Phase 2)
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["cost", "spending", "expense"]):
                return await self._handle_cost_query(query, context)
            elif any(word in query_lower for word in ["optimize", "save", "reduce"]):
                return await self._handle_optimization_query(query, context)
            elif any(word in query_lower for word in ["resource", "instance", "service"]):
                return await self._handle_resource_query(query, context)
            else:
                return await self._handle_general_query(query, context)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "I encountered an error processing your query. Please try again.",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def analyze_data(self, data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Analyze data and provide insights"""
        try:
            insights = []
            recommendations = []
            
            # Analyze cost data
            if "cost_data" in data:
                cost_tool = self.get_tool("cost_analysis")
                if cost_tool:
                    result = await cost_tool.execute({
                        "time_period": "last_30_days",
                        "analysis_type": "trend"
                    }, context)
                    insights.extend(result.get("insights", []))
            
            # Generate optimization recommendations
            opt_tool = self.get_tool("optimization_recommendations")
            if opt_tool:
                result = await opt_tool.execute({
                    "risk_tolerance": "medium",
                    "min_savings": 100
                }, context)
                recommendations.extend(result.get("recommendations", []))
            
            return {
                "insights": insights,
                "recommendations": recommendations,
                "confidence": 0.8,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return {
                "error": str(e),
                "confidence": 0.0,
                "status": "failed"
            }
    
    async def _handle_cost_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Handle cost-related queries"""
        cost_tool = self.get_tool("cost_analysis")
        if cost_tool:
            result = await cost_tool.execute({
                "time_period": "last_30_days",
                "analysis_type": "trend"
            }, context)
            
            insights = result.get("insights", [])
            response = f"Based on your cost data analysis: {'. '.join(insights[:3])}"
            
            return {
                "response": response,
                "data": result,
                "confidence": 0.8
            }
        
        return {
            "response": "I can help you analyze your cloud costs. However, the cost analysis tool is not available right now.",
            "confidence": 0.3
        }
    
    async def _handle_optimization_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Handle optimization-related queries"""
        opt_tool = self.get_tool("optimization_recommendations")
        if opt_tool:
            result = await opt_tool.execute({
                "risk_tolerance": "medium",
                "min_savings": 50
            }, context)
            
            recommendations = result.get("recommendations", [])
            total_savings = result.get("total_potential_savings", 0)
            
            response = f"I found {len(recommendations)} optimization opportunities that could save you ${total_savings:.2f} per month."
            
            return {
                "response": response,
                "recommendations": recommendations,
                "data": result,
                "confidence": 0.85
            }
        
        return {
            "response": "I can help you optimize your cloud costs. However, the optimization tool is not available right now.",
            "confidence": 0.3
        }
    
    async def _handle_resource_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Handle resource-related queries"""
        discovery_tool = self.get_tool("resource_discovery")
        if discovery_tool:
            result = await discovery_tool.execute({
                "providers": ["aws", "gcp", "azure"],
                "include_costs": True
            }, context)
            
            total_resources = result.get("total_resources", 0)
            total_cost = result.get("total_monthly_cost", 0)
            
            response = f"I found {total_resources} cloud resources with a total monthly cost of ${total_cost:.2f}."
            
            return {
                "response": response,
                "data": result,
                "confidence": 0.8
            }
        
        return {
            "response": "I can help you discover and analyze your cloud resources. However, the discovery tool is not available right now.",
            "confidence": 0.3
        }
    
    async def _handle_general_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "response": f"I received your query: '{query}'. I specialize in cloud cost optimization. Ask me about cost analysis, optimization recommendations, or resource discovery.",
            "confidence": 0.6
        }
