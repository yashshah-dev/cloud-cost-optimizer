from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
import os
import httpx
import time
import uuid

# Ensure all loggers are set to INFO level
logging.getLogger().setLevel(logging.INFO)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LocalLLMAgent:
    """
    Local LLM agent using Ollama with Llama 3 for cost optimization tasks.
    Provides natural language explanations and reasoning for optimization recommendations.
    """

    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        logger.info(f"Initializing LocalLLMAgent with model: {model_name}, URL: {self.ollama_url}")

    async def explain_optimization(self, optimization: Dict[str, Any],
                           resource: Dict[str, Any],
                           risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate natural language explanation for an optimization recommendation.

        Args:
            optimization: Optimization recommendation details
            resource: Resource information
            risk_assessment: Risk assessment results

        Returns:
            Explanation with reasoning and recommendations
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] === STARTING LocalLLMAgent.explain_optimization ===")
        logger.info(f"[{request_id}] Input optimization: {optimization.get('title', 'Unknown')}")
        logger.info(f"[{request_id}] Input resource: {resource.get('name', 'Unknown')}")
        logger.info(f"[{request_id}] Input risk level: {risk_assessment.get('risk_level', 'Unknown')}")
        start_time = time.time()

        try:
            # Step 1: Prepare the prompt template
            logger.info(f"[{request_id}] Step 1: Preparing prompt template")
            template = """
            You are a cloud cost optimization expert. Explain this optimization recommendation in simple, business-friendly terms.

            OPTIMIZATION DETAILS:
            Type: {opt_type}
            Title: {opt_title}
            Description: {opt_description}
            Potential Savings: ${potential_savings:.2f} per month
            Confidence: {confidence:.1%}
            Implementation Complexity: {complexity}

            RESOURCE INFORMATION:
            Type: {resource_type}
            Name: {resource_name}
            Current Cost: ${current_cost:.2f} per month
            Provider: {provider}

            RISK ASSESSMENT:
            Risk Level: {risk_level}
            Risk Score: {risk_score:.2f}
            Key Risk Factors: {risk_factors}

            Please provide a structured explanation starting with the title:

            **Optimization Recommendation: {opt_title}**

            **What it does:**
            [Simple explanation of what this optimization does]

            **Why it's recommended:**
            [Why it's recommended for this specific resource]

            **Business Impact:**
            [Potential business impact, both positive and negative]

            **Monitoring After Implementation:**
            [What to monitor after implementation]

            **Rolling Back the Change:**
            [When to consider rolling back the change]

            Keep each section concise but informative, suitable for both technical and business audiences.
            """
            logger.info(f"[{request_id}] Prompt template prepared")

            # Step 2: Prepare input data for the prompt
            logger.info(f"[{request_id}] Step 2: Preparing input data for prompt")
            risk_factors = ", ".join(risk_assessment.get("assessment_breakdown", {}).get("business_impact", {}).get("factors", []))
            logger.info(f"[{request_id}] Risk factors extracted: {risk_factors}")

            prompt_data = {
                "opt_type": optimization.get("type", "Unknown"),
                "opt_title": optimization.get("title", "Unknown"),
                "opt_description": optimization.get("description", "No description"),
                "potential_savings": optimization.get("potential_savings", 0),
                "confidence": optimization.get("confidence_score", 0),
                "complexity": optimization.get("implementation_complexity", "medium"),
                "resource_type": resource.get("resource_type", "Unknown"),
                "resource_name": resource.get("name", "Unknown"),
                "current_cost": resource.get("monthly_cost", 0),
                "provider": resource.get("provider", "Unknown"),
                "risk_level": risk_assessment.get("risk_level", "medium"),
                "risk_score": risk_assessment.get("overall_risk_score", 0.5),
                "risk_factors": risk_factors or "None identified"
            }
            logger.info(f"[{request_id}] Prompt data prepared: {len(prompt_data)} fields")

            # Step 3: Format the prompt
            logger.info(f"[{request_id}] Step 3: Formatting the prompt")
            prompt = template.format(**prompt_data)
            logger.info(f"[{request_id}] Prompt formatted with length: {len(prompt)} characters")

            # Step 4: Prepare HTTP request to Ollama
            logger.info(f"[{request_id}] Step 4: Preparing HTTP request to Ollama")
            ollama_url = f"{self.ollama_url}/api/generate"
            request_payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 2048,
                    "num_predict": 512
                }
            }
            logger.info(f"[{request_id}] Ollama URL: {ollama_url}")
            logger.info(f"[{request_id}] Model: {self.model_name}")
            logger.info(f"[{request_id}] Request payload size: {len(str(request_payload))} characters")

            # Step 5: Make HTTP request to Ollama
            logger.info(f"[{request_id}] Step 5: Making HTTP request to Ollama")
            http_start = time.time()

            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"[{request_id}] HTTP client created with 30s timeout")
                logger.info(f"[{request_id}] Sending POST request to {ollama_url}")

                response = await client.post(
                    ollama_url,
                    json=request_payload
                )

                http_time = time.time() - http_start
                logger.info(f"[{request_id}] HTTP request completed in {http_time:.3f}s")
                logger.info(f"[{request_id}] Response status code: {response.status_code}")
                logger.info(f"[{request_id}] Response headers: {dict(response.headers)}")

                # Step 6: Process the response
                logger.info(f"[{request_id}] Step 6: Processing Ollama response")
                if response.status_code == 200:
                    logger.info(f"[{request_id}] Response successful, parsing JSON")
                    result = response.json()
                    explanation = result.get("response", "")
                    logger.info(f"[{request_id}] Response parsed successfully")
                    logger.info(f"[{request_id}] Explanation length: {len(explanation)} characters")

                    # Step 7: Prepare final response
                    logger.info(f"[{request_id}] Step 7: Preparing final response")
                    total_time = time.time() - start_time
                    logger.info(f"[{request_id}] === LocalLLMAgent.explain_optimization COMPLETED in {total_time:.3f}s ===")

                    return {
                        "explanation": explanation,
                        "generated_at": datetime.utcnow().isoformat(),
                        "model_used": self.model_name,
                        "confidence": "high"
                    }
                else:
                    logger.error(f"[{request_id}] Ollama API error: {response.status_code}")
                    logger.error(f"[{request_id}] Response text: {response.text[:500]}...")
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    raise Exception(error_msg)

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[{request_id}] ERROR: Exception in LocalLLMAgent.explain_optimization after {total_time:.3f}s")
            logger.error(f"[{request_id}] Exception type: {type(e).__name__}")
            logger.error(f"[{request_id}] Exception message: {str(e)}")
            import traceback
            logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")

            return {
                "error": str(e),
                "explanation": "Unable to generate explanation due to technical issues",
                "generated_at": datetime.utcnow().isoformat()
            }

    def analyze_cost_trends(self, cost_data: List[Dict[str, Any]],
                          time_period: str = "30d") -> Dict[str, Any]:
        """
        Analyze cost trends and provide insights using the local LLM.

        Args:
            cost_data: Historical cost data
            time_period: Analysis time period

        Returns:
            Trend analysis with insights and recommendations
        """
        logger.info("Starting analyze_cost_trends with direct httpx call")
        start_time = time.time()

        try:
            # Summarize cost data
            total_cost = sum(item.get("cost", 0) for item in cost_data)
            avg_daily_cost = total_cost / max(len(cost_data), 1)

            # Group by service
            service_costs = {}
            for item in cost_data:
                service = item.get("service_name", "Unknown")
                service_costs[service] = service_costs.get(service, 0) + item.get("cost", 0)

            top_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]

            template = """
            You are a cost optimization analyst. Analyze these cost trends and provide actionable insights.

            COST SUMMARY:
            Total Cost: ${total_cost:.2f}
            Average Daily Cost: ${avg_daily_cost:.2f}
            Number of Cost Items: {num_items}
            Analysis Period: {time_period}

            TOP COST CENTERS:
            {top_services}

            Please provide:
            1. Key trends and patterns you observe
            2. Potential cost optimization opportunities
            3. Areas that need immediate attention
            4. Recommendations for cost monitoring and control

            Focus on actionable insights that can drive cost savings.
            """

            # Format top services
            services_text = "\n".join([f"- {service}: ${cost:.2f}" for service, cost in top_services])

            prompt = template.format(
                total_cost=total_cost,
                avg_daily_cost=avg_daily_cost,
                num_items=len(cost_data),
                time_period=time_period,
                top_services=services_text
            )

            logger.info(f"Prepared cost analysis prompt with length: {len(prompt)} characters")

            # Make synchronous HTTP call to Ollama
            import httpx
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_ctx": 2048,
                            "num_predict": 512
                        }
                    }
                )
            request_time = time.time() - start_time
            logger.info(f"Ollama HTTP request for cost analysis completed in {request_time:.3f}s")

            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "")
                total_time = time.time() - start_time
                logger.info(f"Successfully generated cost analysis in {total_time:.3f}s, response length: {len(analysis)}")

                return {
                    "analysis": analysis,
                    "summary": {
                        "total_cost": total_cost,
                        "avg_daily_cost": avg_daily_cost,
                        "top_services": top_services
                    },
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_used": self.model_name
                }
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Error analyzing cost trends after {total_time:.3f}s: {e}")
            return {"error": str(e)}

    def generate_optimization_strategy(self, resources: List[Dict[str, Any]],
                                     optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive optimization strategy using the local LLM.

        Args:
            resources: List of resources to optimize
            optimizations: List of optimization recommendations

        Returns:
            Strategic optimization plan with prioritization
        """
        try:
            # Calculate totals
            total_resources = len(resources)
            total_optimizations = len(optimizations)
            total_savings = sum(opt.get("potential_savings", 0) for opt in optimizations)

            # Group optimizations by type
            opt_types = {}
            for opt in optimizations:
                opt_type = opt.get("type", "unknown")
                opt_types[opt_type] = opt_types.get(opt_type, 0) + 1

            template = """
            You are a cloud cost optimization strategist. Create a comprehensive optimization strategy.

            CURRENT STATE:
            Total Resources: {total_resources}
            Optimization Opportunities: {total_optimizations}
            Total Potential Savings: ${total_savings:.2f} per month

            OPTIMIZATION BREAKDOWN:
            {opt_breakdown}

            Please create a strategic plan that includes:
            1. Overall optimization approach and timeline
            2. Prioritization strategy for different optimization types
            3. Risk mitigation strategies
            4. Implementation phases and milestones
            5. Success metrics and monitoring approach
            6. Long-term cost governance recommendations

            Focus on practical, phased implementation that balances speed and safety.
            """

            # Format optimization breakdown
            breakdown_text = "\n".join([f"- {opt_type}: {count} opportunities" for opt_type, count in opt_types.items()])

            prompt = template.format(
                total_resources=total_resources,
                total_optimizations=total_optimizations,
                total_savings=total_savings,
                opt_breakdown=breakdown_text
            )

            # Make HTTP request to Ollama
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_ctx": 2048,
                            "num_predict": 512
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    strategy_text = result.get("response", "")

                    return {
                        "strategy": strategy_text,
                        "summary": {
                            "total_resources": total_resources,
                            "total_optimizations": total_optimizations,
                            "total_savings": total_savings,
                            "optimization_types": opt_types
                        },
                        "generated_at": datetime.utcnow().isoformat(),
                        "model_used": self.model_name
                    }
                else:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"error": error_msg}

        except Exception as e:
            logger.error(f"Error generating optimization strategy: {e}")
            return {"error": str(e)}

    def answer_cost_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer general cost optimization questions using the local LLM.

        Args:
            question: User's question about cost optimization
            context: Relevant context data

        Returns:
            Answer with reasoning and recommendations
        """
        try:
            template = """
            You are a cloud cost optimization expert. Answer this question based on the provided context.

            QUESTION: {question}

            CONTEXT:
            {context}

            Please provide:
            1. A clear, direct answer to the question
            2. Supporting reasoning based on best practices
            3. Any relevant examples or scenarios
            4. Additional recommendations if applicable

            Keep your response focused and actionable.
            """

            # Format context
            context_text = json.dumps(context, indent=2)

            prompt = template.format(
                question=question,
                context=context_text
            )

            # Make HTTP request to Ollama
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_ctx": 2048,
                            "num_predict": 512
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    answer_text = result.get("response", "")

                    return {
                        "answer": answer_text,
                        "question": question,
                        "generated_at": datetime.utcnow().isoformat(),
                        "model_used": self.model_name
                    }
                else:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"error": error_msg}

        except Exception as e:
            logger.error(f"Error answering cost question: {e}")
            return {"error": str(e)}

    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different Ollama model for cost optimization.
        Useful for using smaller models when cost is a priority.

        Args:
            model_name: Name of the Ollama model to switch to

        Returns:
            True if switch was successful, False otherwise
        """
        try:
            old_model = self.model_name
            
            # Check if new model is available by trying to use it
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": "Test prompt",
                            "stream": False,
                            "options": {"num_predict": 1}
                        }
                    )
                    
                if response.status_code == 200:
                    self.model_name = model_name
                    logger.info(f"Successfully switched from {old_model} to {model_name}")
                    return True
                else:
                    logger.error(f"Failed to switch to {model_name}, model not available")
                    return False
                    
            except Exception as e:
                logger.error(f"Error testing new model {model_name}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            return False

    def get_cost_efficient_models(self) -> List[str]:
        """
        Get list of cost-efficient models available locally.
        Prioritizes smaller, faster models for cost optimization tasks.
        """
        efficient_models = [
            "llama3.2",      # Most cost-effective, good performance
            "phi3",          # Microsoft's efficient model
            "mistral",       # Good balance of size and performance
            "qwen2",         # Alibaba's efficient model
            "llama3"         # Fallback to larger model if needed
        ]

        # Check which models are actually available
        available_models = []
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                available_names = [line.split()[0] for line in lines if line.strip()]

                # Filter to efficient models that are available
                available_models = [model for model in efficient_models if model in available_names]
        except Exception as e:
            logger.warning(f"Could not check available models: {e}")

        return available_models or ["llama3.2"]  # Default fallback

    def is_available(self) -> bool:
        """Check if the local LLM is available and responding."""
        try:
            # Try to make a simple health check request to Ollama
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"LLM availability check failed: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the local LLM model."""
        return {
            "model_name": self.model_name,
            "provider": "Ollama",
            "type": "Local LLM",
            "available": self.is_available(),
            "cost_efficient": self.model_name in ["llama3.2", "phi3", "mistral", "qwen2"],
            "last_checked": datetime.utcnow().isoformat()
        }
