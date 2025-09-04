#!/usr/bin/env python3
"""
ML Pipeline Runner for Cloud Cost Optimization

This script runs the complete ML pipeline for generating cloud cost optimization recommendations.
"""

import asyncio
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add the backend directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent))

from app.ml_pipeline import CloudCostOptimizationPipeline, MLPipelineConfig
from app.database import async_session_maker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run_ml_pipeline(resource_ids=None, config=None):
    """
    Run the ML pipeline with the given configuration.

    Args:
        resource_ids: Optional list of specific resource IDs to analyze
        config: Pipeline configuration
    """
    try:
        logger.info("Initializing ML pipeline...")

        # Create pipeline instance
        pipeline = CloudCostOptimizationPipeline(config)

        # Run the pipeline
        logger.info("Starting pipeline execution...")
        results = await pipeline.run_pipeline(resource_ids)

        # Log results
        if results["status"] == "success":
            logger.info("✅ ML pipeline completed successfully!")
            logger.info(f"📊 Generated {len(results['recommendations'])} recommendations")
            logger.info(f"💰 Total potential savings: ${results['summary']['total_potential_savings']:.2f}")
            logger.info(f"⏱️  Total execution time: {results['total_duration']:.2f} seconds")

            # Save recommendations to database
            if results["recommendations"]:
                logger.info("💾 Saving recommendations to database...")
                save_result = await pipeline.save_recommendations_to_db(results["recommendations"])
                if save_result["status"] == "success":
                    logger.info(f"✅ Saved {save_result['saved_count']} recommendations to database")
                else:
                    logger.error(f"❌ Failed to save recommendations: {save_result['error']}")

        else:
            logger.error(f"❌ ML pipeline failed: {results['message']}")
            if results.get("error"):
                logger.error(f"Error details: {results['error']}")

        # Save detailed results to file
        output_file = f"ml_pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Detailed results saved to {output_file}")

        return results

    except Exception as e:
        logger.error(f"❌ Fatal error running ML pipeline: {e}")
        return {
            "status": "error",
            "message": "Fatal pipeline error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run ML Pipeline for Cloud Cost Optimization')

    parser.add_argument(
        '--resource-ids',
        nargs='+',
        help='Specific resource IDs to analyze (optional)'
    )

    parser.add_argument(
        '--analysis-window',
        type=int,
        default=30,
        help='Analysis window in days (default: 30)'
    )

    parser.add_argument(
        '--min-data-points',
        type=int,
        default=7,
        help='Minimum data points required per resource (default: 7)'
    )

    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.6,
        help='Minimum confidence threshold for recommendations (default: 0.6)'
    )

    parser.add_argument(
        '--max-recommendations',
        type=int,
        default=3,
        help='Maximum recommendations per resource (default: 3)'
    )

    parser.add_argument(
        '--disable-anomaly-detection',
        action='store_true',
        help='Disable anomaly detection'
    )

    parser.add_argument(
        '--disable-risk-assessment',
        action='store_true',
        help='Disable risk assessment'
    )

    parser.add_argument(
        '--disable-performance-prediction',
        action='store_true',
        help='Disable performance prediction'
    )

    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_arguments()

    # Create pipeline configuration
    config = MLPipelineConfig(
        analysis_window_days=args.analysis_window,
        min_data_points=args.min_data_points,
        confidence_threshold=args.confidence_threshold,
        max_recommendations_per_resource=args.max_recommendations,
        enable_anomaly_detection=not args.disable_anomaly_detection,
        enable_risk_assessment=not args.disable_risk_assessment,
        enable_performance_prediction=not args.disable_performance_prediction
    )

    logger.info("🚀 Starting Cloud Cost Optimization ML Pipeline")
    logger.info(f"Configuration: {config.__dict__}")

    if args.resource_ids:
        logger.info(f"Analyzing specific resources: {args.resource_ids}")
    else:
        logger.info("Analyzing all available resources")

    # Run the pipeline
    results = await run_ml_pipeline(args.resource_ids, config)

    # Print summary
    print("\n" + "="*60)
    print("ML PIPELINE EXECUTION SUMMARY")
    print("="*60)

    if results["status"] == "success":
        print("✅ Status: SUCCESS")
        print(f"📊 Recommendations Generated: {len(results['recommendations'])}")
        print(f"💰 Total Potential Savings: ${results['summary']['total_potential_savings']:.2f}")
        print(f"⏱️  Execution Time: {results['total_duration']:.2f} seconds")
        print(f"📈 Stages Completed: {results['stages_completed']}/{results['total_stages']}")

        # Show top recommendations
        if results["recommendations"]:
            print("\n🏆 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(results["recommendations"][:5], 1):
                print(f"{i}. {rec['title']} - ${rec.get('potential_savings', 0):.2f} savings")

    else:
        print("❌ Status: FAILED")
        print(f"Message: {results['message']}")
        if results.get("error"):
            print(f"Error: {results['error']}")

    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
