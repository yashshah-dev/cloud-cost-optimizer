from typing import Dict, Any, List, Optional
import logging
import uuid
import time
from datetime import datetime
from .local_llm_agent import LocalLLMAgent
from ..ml.usage_analyzer import UsagePatternAnalyzer
from ..ml.risk_assessor import RiskAssessor
from ..ml.recommender import OptimizationRecommender
from ..ml.predictor import PerformancePredictor

logger = logging.getLogger(__name__)

class OptimizationTools:
    """
    Tools for the AI agent to interact with optimization components.
    Provides interfaces to ML models and analysis functions.
    """

    def __init__(self):
        self.llm_agent = LocalLLMAgent()
        # Initialize ML components
        self.usage_analyzer = UsagePatternAnalyzer()
        self.risk_assessor = RiskAssessor()
        self.recommender = OptimizationRecommender()
        self.predictor = PerformancePredictor()
        self.tools = {}
        self.cost_metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "cost_savings": 0
        }
        self._register_tools()

    def _register_tools(self):
        """Register available tools for the agent."""
        self.tools = {
            "analyze_usage_patterns": self.analyze_usage_patterns,
            "assess_risks": self.assess_risks,
            "generate_recommendations": self.generate_recommendations,
            "predict_performance": self.predict_performance,
            "explain_optimization": self.explain_optimization,
            "analyze_cost_trends": self.analyze_cost_trends,
            "generate_strategy": self.generate_strategy,
            "answer_question": self.answer_question
        }

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        try:
            import time
            start_time = time.time()

            tool_func = self.tools[tool_name]
            result = tool_func(**parameters)

            execution_time = time.time() - start_time

            # Update cost metrics
            self.cost_metrics["total_requests"] += 1
            self.cost_metrics["avg_response_time"] = (
                (self.cost_metrics["avg_response_time"] * (self.cost_metrics["total_requests"] - 1)) +
                execution_time
            ) / self.cost_metrics["total_requests"]

            return {
                "tool": tool_name,
                "result": result,
                "executed_at": datetime.utcnow().isoformat(),
                "execution_time": execution_time,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "tool": tool_name,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat(),
                "success": False
            }

    def analyze_usage_patterns(self, resource_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze usage patterns for resources."""
        try:
            # Convert resource data to the format expected by the analyzer
            usage_data = []
            for resource in resource_data:
                # Extract usage metrics from resource data
                usage_entry = {
                    "resource_id": resource.get("id"),
                    "timestamp": resource.get("timestamp", datetime.utcnow().isoformat()),
                    "cpu_utilization": resource.get("cpu_utilization", 0),
                    "memory_utilization": resource.get("memory_utilization", 0),
                    "network_in": resource.get("network_in", 0),
                    "network_out": resource.get("network_out", 0),
                    "disk_read_ops": resource.get("disk_read_ops", 0),
                    "disk_write_ops": resource.get("disk_write_ops", 0)
                }
                usage_data.append(usage_entry)

            # Analyze patterns using the ML component
            analysis_result = self.usage_analyzer.analyze_patterns(usage_data)

            return {
                "analysis_type": "usage_patterns",
                "resources_analyzed": len(resource_data),
                "patterns_found": analysis_result.get("patterns", []),
                "anomalies_detected": analysis_result.get("anomalies", []),
                "recommendations": analysis_result.get("recommendations", []),
                "confidence_scores": analysis_result.get("confidence_scores", {}),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            return {
                "error": str(e),
                "analysis_type": "usage_patterns",
                "resources_analyzed": len(resource_data)
            }

    def assess_risks(self, resource: Dict[str, Any], optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks for an optimization."""
        try:
            # Assess risk using the ML component
            risk_assessment = self.risk_assessor.assess_risk(resource, optimization)

            return {
                "risk_level": risk_assessment.get("risk_level", "medium"),
                "risk_score": risk_assessment.get("overall_risk_score", 0.5),
                "assessment_breakdown": risk_assessment.get("assessment_breakdown", {}),
                "recommendations": risk_assessment.get("recommendations", []),
                "mitigation_strategies": risk_assessment.get("mitigation_strategies", []),
                "rollback_plan": risk_assessment.get("rollback_plan", {}),
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {
                "error": str(e),
                "risk_level": "unknown",
                "risk_score": 0.5
            }

    def generate_recommendations(self, resources: List[Dict[str, Any]],
                               usage_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        try:
            # Generate recommendations using the ML component
            recommendations = self.recommender.generate_recommendations(resources, usage_data)

            # Enhance recommendations with additional context
            enhanced_recommendations = []
            for rec in recommendations:
                # Add risk assessment for each recommendation
                resource = next((r for r in resources if r.get("id") == rec.get("resource_id")), {})
                if resource:
                    risk_assessment = self.risk_assessor.assess_risk(resource, rec)
                    rec["risk_assessment"] = risk_assessment

                # Add performance prediction
                usage_patterns = self._extract_usage_patterns_for_resource(
                    rec.get("resource_id"), usage_data
                )
                if usage_patterns:
                    performance_prediction = self.predictor.predict_impact(
                        resource, rec, usage_patterns
                    )
                    rec["performance_prediction"] = performance_prediction

                enhanced_recommendations.append(rec)

            return enhanced_recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def predict_performance(self, resource: Dict[str, Any],
                          optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance impact."""
        try:
            # Extract usage patterns for the resource
            usage_patterns = self._extract_usage_patterns_for_resource(
                resource.get("id"), []
            )

            # Predict performance using the ML component
            prediction = self.predictor.predict_impact(resource, optimization, usage_patterns)

            return prediction

        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return {
                "error": str(e),
                "predicted_performance_impact": 0.0,
                "confidence_level": "low"
            }

    async def explain_optimization(self, optimization: Dict[str, Any],
                           resource: Dict[str, Any]) -> Dict[str, Any]:
        """Generate natural language explanation."""
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] === STARTING OptimizationTools.explain_optimization ===")
        logger.info(f"[{request_id}] Input optimization: {optimization.get('title', 'Unknown')} (type: {optimization.get('type', 'Unknown')})")
        logger.info(f"[{request_id}] Input resource: {resource.get('name', 'Unknown')} (type: {resource.get('resource_type', 'Unknown')})")
        start_time = time.time()

        try:
            # Step 1: Assess risk for the optimization
            logger.info(f"[{request_id}] Step 1: Assessing risk for optimization")
            risk_start = time.time()
            risk_assessment = self.risk_assessor.assess_risk(resource, optimization)
            risk_time = time.time() - risk_start
            logger.info(f"[{request_id}] Risk assessment completed in {risk_time:.3f}s")
            logger.info(f"[{request_id}] Risk assessment result: level={risk_assessment.get('risk_level', 'unknown')}, score={risk_assessment.get('overall_risk_score', 'unknown')}")

            # Step 2: Check LLM availability
            logger.info(f"[{request_id}] Step 2: Checking LLM availability")
            llm_available = self.llm_agent.is_available()
            logger.info(f"[{request_id}] LLM availability: {llm_available}")

            if not llm_available:
                logger.warning(f"[{request_id}] LLM not available, returning fallback response")
                fallback_response = {
                    "explanation": "This optimization will help reduce costs by optimizing resource usage.",
                    "llm_available": False,
                    "risk_assessment": risk_assessment
                }
                total_time = time.time() - start_time
                logger.info(f"[{request_id}] Fallback response prepared in {total_time:.3f}s")
                return fallback_response

            # Step 3: Call LLM agent for explanation
            logger.info(f"[{request_id}] Step 3: Calling LLM agent for explanation")
            llm_start = time.time()
            logger.info(f"[{request_id}] Invoking self.llm_agent.explain_optimization()")

            explanation = await self.llm_agent.explain_optimization(optimization, resource, risk_assessment)

            llm_time = time.time() - llm_start
            logger.info(f"[{request_id}] LLM agent call completed in {llm_time:.3f}s")
            logger.info(f"[{request_id}] LLM response type: {type(explanation)}")
            logger.info(f"[{request_id}] LLM response keys: {list(explanation.keys()) if isinstance(explanation, dict) else 'Not a dict'}")

            # Step 4: Validate and return response
            logger.info(f"[{request_id}] Step 4: Validating and returning response")
            total_time = time.time() - start_time
            logger.info(f"[{request_id}] === OptimizationTools.explain_optimization COMPLETED in {total_time:.3f}s ===")

            return explanation

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[{request_id}] ERROR: Exception in OptimizationTools.explain_optimization after {total_time:.3f}s")
            logger.error(f"[{request_id}] Exception type: {type(e).__name__}")
            logger.error(f"[{request_id}] Exception message: {str(e)}")
            import traceback
            logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")

            return {
                "error": str(e),
                "explanation": "Unable to generate explanation",
                "llm_available": self.llm_agent.is_available()
            }

    def analyze_cost_trends(self, cost_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cost trends."""
        if not self.llm_agent.is_available():
            return {
                "analysis": "Cost trends show potential for optimization.",
                "llm_available": False
            }

        return self.llm_agent.analyze_cost_trends(cost_data)

    def generate_strategy(self, resources: List[Dict[str, Any]],
                        optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate optimization strategy."""
        if not self.llm_agent.is_available():
            return {
                "strategy": "Implement optimizations in phases, starting with low-risk changes.",
                "llm_available": False
            }

        return self.llm_agent.generate_optimization_strategy(resources, optimizations)

    def answer_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Answer cost optimization questions."""
        if not self.llm_agent.is_available():
            return {
                "answer": "For cost optimization questions, consider rightsizing and using reserved instances.",
                "llm_available": False
            }

        return self.llm_agent.answer_cost_question(question, context)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of the AI agent and its tools."""
        return {
            "llm_available": self.llm_agent.is_available(),
            "llm_model": self.llm_agent.get_model_info(),
            "available_tools": self.get_available_tools(),
            "cost_metrics": self.cost_metrics,
            "last_checked": datetime.utcnow().isoformat()
        }

    def optimize_for_cost(self) -> Dict[str, Any]:
        """
        Optimize the LLM agent for cost efficiency.
        Switches to smaller models and adjusts parameters for lower resource usage.
        """
        try:
            # Get available cost-efficient models
            efficient_models = self.llm_agent.get_cost_efficient_models()

            if not efficient_models:
                return {"error": "No cost-efficient models available"}

            # Try to switch to the most efficient available model
            current_model = self.llm_agent.model_name
            for model in efficient_models:
                if model != current_model:
                    if self.llm_agent.switch_model(model):
                        logger.info(f"Switched to cost-efficient model: {model}")
                        return {
                            "success": True,
                            "new_model": model,
                            "previous_model": current_model,
                            "cost_savings": "estimated_30_50_percent"
                        }

            return {
                "success": False,
                "message": "Already using the most cost-efficient available model",
                "current_model": current_model
            }

        except Exception as e:
            logger.error(f"Error optimizing for cost: {e}")
            return {"error": str(e)}

    def get_cost_metrics(self) -> Dict[str, Any]:
        """Get cost and performance metrics for the agent."""
        return {
            "total_requests": self.cost_metrics["total_requests"],
            "average_response_time": f"{self.cost_metrics['avg_response_time']:.2f}s",
            "estimated_tokens_used": self.cost_metrics["total_tokens"],
            "cost_savings_generated": f"${self.cost_metrics['cost_savings']:.2f}",
            "model_info": self.llm_agent.get_model_info(),
            "efficiency_score": self._calculate_efficiency_score()
        }

    def _calculate_efficiency_score(self) -> float:
        """Calculate an efficiency score based on performance and cost metrics."""
        if self.cost_metrics["total_requests"] == 0:
            return 0.0

        # Efficiency based on response time and success rate
        avg_time = self.cost_metrics["avg_response_time"]
        efficiency = max(0, 1 - (avg_time / 10))  # Penalize slow responses

        return round(efficiency, 2)

    def reset_cost_metrics(self) -> Dict[str, Any]:
        """Reset cost metrics for fresh monitoring."""
        self.cost_metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "cost_savings": 0
        }
        return {"message": "Cost metrics reset successfully"}

    def _extract_usage_patterns_for_resource(self, resource_id: str,
                                           usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract usage patterns for a specific resource."""
        try:
            # Filter usage data for the specific resource
            resource_usage = [u for u in usage_data if u.get("resource_id") == resource_id]

            if not resource_usage:
                return {}

            # Calculate basic statistics
            cpu_values = [u.get("cpu_utilization", 0) for u in resource_usage]
            memory_values = [u.get("memory_utilization", 0) for u in resource_usage]

            return {
                "avg_cpu_utilization": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "avg_memory_utilization": sum(memory_values) / len(memory_values) if memory_values else 0,
                "peak_cpu_utilization": max(cpu_values) if cpu_values else 0,
                "peak_memory_utilization": max(memory_values) if memory_values else 0,
                "cpu_variance": self._calculate_variance(cpu_values),
                "data_points": len(resource_usage)
            }

        except Exception as e:
            logger.error(f"Error extracting usage patterns: {e}")
            return {}

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
