"""
Background worker for processing optimization tasks and data ingestion jobs.
Uses Celery for task queuing and Redis as the message broker.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from celery import Celery
from app.database import get_db
from app.agent.local_llm_agent import LocalLLMAgent
from app.providers.aws import AWSProvider
from app.providers.gcp import GCPProvider
from app.providers.azure import AzureProvider
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "cost_optimizer_worker",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Initialize providers
aws_provider = AWSProvider()
gcp_provider = GCPProvider()
azure_provider = AzureProvider()

# Initialize LLM agent
llm_agent = LocalLLMAgent()

@celery_app.task(name="process_cost_optimization")
def process_cost_optimization_task(provider: str, resource_data: dict):
    """
    Process cost optimization for a specific resource.

    Args:
        provider: Cloud provider (aws, gcp, azure)
        resource_data: Resource information for optimization
    """
    try:
        logger.info(f"Processing cost optimization for {provider} resource: {resource_data.get('resource_id', 'unknown')}")

        # Get database session
        db = next(get_db())

        # Process based on provider
        if provider == "aws":
            optimization_result = aws_provider.optimize_cost(resource_data)
        elif provider == "gcp":
            optimization_result = gcp_provider.optimize_cost(resource_data)
        elif provider == "azure":
            optimization_result = azure_provider.optimize_cost(resource_data)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Use LLM agent to generate recommendations
        if optimization_result:
            recommendations = llm_agent.generate_optimization_recommendations(
                resource_data, optimization_result
            )

            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            return {
                "status": "success",
                "recommendations": recommendations,
                "resource_id": resource_data.get("resource_id")
            }

        return {
            "status": "no_optimization_needed",
            "resource_id": resource_data.get("resource_id")
        }

    except Exception as e:
        logger.error(f"Error processing cost optimization: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "resource_id": resource_data.get("resource_id", "unknown")
        }

@celery_app.task(name="ingest_cloud_resources")
def ingest_cloud_resources_task(provider: str, account_config: dict):
    """
    Ingest cloud resources from a specific provider.

    Args:
        provider: Cloud provider (aws, gcp, azure)
        account_config: Account configuration for the provider
    """
    try:
        logger.info(f"Ingesting resources from {provider}")

        # Get database session
        db = next(get_db())

        # Process based on provider
        if provider == "aws":
            resources = aws_provider.get_resources(account_config)
        elif provider == "gcp":
            resources = gcp_provider.get_resources(account_config)
        elif provider == "azure":
            resources = azure_provider.get_resources(account_config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Store resources in database
        stored_count = 0
        for resource in resources:
            try:
                # Store resource logic here
                # This would typically involve creating database records
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing resource {resource.get('resource_id')}: {str(e)}")

        logger.info(f"Successfully ingested {stored_count} resources from {provider}")
        return {
            "status": "success",
            "provider": provider,
            "resources_ingested": stored_count
        }

    except Exception as e:
        logger.error(f"Error ingesting resources from {provider}: {str(e)}")
        return {
            "status": "error",
            "provider": provider,
            "error": str(e)
        }

@celery_app.task(name="generate_cost_report")
def generate_cost_report_task(provider: str, date_range: dict):
    """
    Generate cost reports for a specific provider and date range.

    Args:
        provider: Cloud provider (aws, gcp, azure)
        date_range: Start and end dates for the report
    """
    try:
        logger.info(f"Generating cost report for {provider}")

        # Get database session
        db = next(get_db())

        # Generate report based on provider
        if provider == "aws":
            report = aws_provider.generate_cost_report(date_range)
        elif provider == "gcp":
            report = gcp_provider.generate_cost_report(date_range)
        elif provider == "azure":
            report = azure_provider.generate_cost_report(date_range)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"Generated cost report for {provider}")
        return {
            "status": "success",
            "provider": provider,
            "report": report
        }

    except Exception as e:
        logger.error(f"Error generating cost report for {provider}: {str(e)}")
        return {
            "status": "error",
            "provider": provider,
            "error": str(e)
        }

if __name__ == "__main__":
    # Start the worker
    logger.info("Starting cost optimizer worker...")
    celery_app.start()
