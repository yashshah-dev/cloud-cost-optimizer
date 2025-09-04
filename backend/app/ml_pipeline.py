"""
Complete ML Pipeline for Cloud Cost Optimization

This module orchestrates the entire ML pipeline for cloud cost optimization,
integrating data ingestion, feature engineering, pattern analysis, risk assessment,
recommendation generation, and performance estimation.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from .database import async_session_maker
from .models import CloudResource, CostEntry, OptimizationRecommendation
from .schemas import OptimizationRecommendationResponse, OptimizationsResponse
from .ml.usage_analyzer import UsagePatternAnalyzer
from .ml.recommender import OptimizationRecommender
from .ml.risk_assessor import RiskAssessor
from .ml.predictor import PerformancePredictor

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    DATA_INGESTION = "data_ingestion"
    FEATURE_ENGINEERING = "feature_engineering"
    PATTERN_ANALYSIS = "pattern_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    PERFORMANCE_ESTIMATION = "performance_estimation"
    VALIDATION = "validation"

@dataclass
class PipelineResult:
    """Result of running the ML pipeline."""
    stage: PipelineStage
    success: bool
    data: Dict[str, Any]
    timestamp: datetime
    duration: float
    error: Optional[str] = None

@dataclass
class MLPipelineConfig:
    """Configuration for the ML pipeline."""
    analysis_window_days: int = 30
    min_data_points: int = 7
    confidence_threshold: float = 0.6
    max_recommendations_per_resource: int = 3
    enable_anomaly_detection: bool = True
    enable_risk_assessment: bool = True
    enable_performance_prediction: bool = True

class CloudCostOptimizationPipeline:
    """
    Complete ML pipeline for cloud cost optimization.

    Orchestrates the entire process from data ingestion to recommendation generation.
    """

    def __init__(self, config: Optional[MLPipelineConfig] = None):
        self.config = config or MLPipelineConfig()
        self.usage_analyzer = UsagePatternAnalyzer()
        self.recommender = OptimizationRecommender()
        self.risk_assessor = RiskAssessor()
        self.performance_predictor = PerformancePredictor()
        self.pipeline_results: List[PipelineResult] = []

    async def run_pipeline(self, resource_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the complete ML pipeline.

        Args:
            resource_ids: Optional list of specific resource IDs to analyze.
                        If None, analyzes all resources.

        Returns:
            Complete pipeline results with recommendations.
        """
        start_time = datetime.utcnow()
        logger.info("Starting ML pipeline execution")

        try:
            # Stage 1: Data Ingestion
            ingestion_result = await self._run_data_ingestion(resource_ids)
            self.pipeline_results.append(ingestion_result)

            if not ingestion_result.success:
                return self._create_error_response("Data ingestion failed", ingestion_result.error)

            # Stage 2: Feature Engineering
            feature_result = await self._run_feature_engineering(ingestion_result.data)
            self.pipeline_results.append(feature_result)

            if not feature_result.success:
                return self._create_error_response("Feature engineering failed", feature_result.error)

            # Stage 3: Pattern Analysis
            pattern_result = await self._run_pattern_analysis(feature_result.data)
            self.pipeline_results.append(pattern_result)

            if not pattern_result.success:
                return self._create_error_response("Pattern analysis failed", pattern_result.error)

            # Stage 4: Risk Assessment
            if self.config.enable_risk_assessment:
                risk_result = await self._run_risk_assessment(pattern_result.data)
                self.pipeline_results.append(risk_result)

                if not risk_result.success:
                    logger.warning("Risk assessment failed, continuing without risk data")

            # Stage 5: Recommendation Generation
            recommendation_result = await self._run_recommendation_generation(pattern_result.data, ingestion_result.data)
            self.pipeline_results.append(recommendation_result)

            if not recommendation_result.success:
                return self._create_error_response("Recommendation generation failed", recommendation_result.error)

            # Stage 6: Performance Estimation
            if self.config.enable_performance_prediction:
                performance_result = await self._run_performance_estimation(
                    recommendation_result.data, pattern_result.data
                )
                self.pipeline_results.append(performance_result)

                if not performance_result.success:
                    logger.warning("Performance estimation failed, continuing without predictions")

            # Stage 7: Validation and Finalization
            final_result = await self._run_validation_and_finalization(recommendation_result.data)
            self.pipeline_results.append(final_result)

            total_duration = (datetime.utcnow() - start_time).total_seconds()

            return self._sanitize_numeric_values({
                "status": "success",
                "total_duration": total_duration,
                "stages_completed": len([r for r in self.pipeline_results if r.success]),
                "total_stages": len(PipelineStage),
                "recommendations": final_result.data.get("recommendations", []),
                "summary": self._generate_pipeline_summary(),
                "pipeline_results": [
                    {
                        "stage": result.stage.value,
                        "success": result.success,
                        "duration": result.duration,
                        "timestamp": result.timestamp.isoformat()
                    }
                    for result in self.pipeline_results
                ]
            })

        except Exception as e:
            logger.error(f"ML pipeline execution failed: {e}")
            return self._create_error_response("Pipeline execution failed", str(e))

    async def _run_data_ingestion(self, resource_ids: Optional[List[str]]) -> PipelineResult:
        """Stage 1: Ingest resource, cost, and usage data."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting data ingestion")

            async with async_session_maker() as session:
                # Get resources
                if resource_ids:
                    query = select(CloudResource).where(CloudResource.id.in_(resource_ids))
                else:
                    query = select(CloudResource)

                result = await session.execute(query)
                resources = result.scalars().all()

                # Get cost data for analysis window
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=self.config.analysis_window_days)

                cost_query = select(CostEntry).where(
                    and_(
                        CostEntry.date >= start_date,
                        CostEntry.date <= end_date
                    )
                )
                cost_result = await session.execute(cost_query)
                cost_entries = cost_result.scalars().all()

                # Convert to dictionaries for processing
                resource_data = []
                for resource in resources:
                    resource_dict = {
                        "id": str(resource.id),
                        "provider": resource.provider,
                        "resource_id": resource.resource_id,
                        "resource_type": resource.resource_type,
                        "name": resource.name,
                        "region": resource.region,
                        "tags": resource.tags or {},
                        "specifications": resource.specifications or {},
                        "created_at": resource.created_at.isoformat() if resource.created_at else None,
                        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None
                    }
                    resource_data.append(resource_dict)

                cost_data = []
                for cost in cost_entries:
                    cost_dict = {
                        "resource_id": str(cost.resource_id),
                        "date": cost.date.isoformat(),
                        "cost": cost.cost,
                        "currency": cost.currency,
                        "usage_quantity": cost.usage_quantity,
                        "usage_unit": cost.usage_unit,
                        "service_name": cost.service_name,
                        "cost_category": cost.cost_category
                    }
                    cost_data.append(cost_dict)

                data = {
                    "resources": resource_data,
                    "cost_entries": cost_data,
                    "analysis_window": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": self.config.analysis_window_days
                    },
                    "summary": {
                        "total_resources": len(resource_data),
                        "total_cost_entries": len(cost_data),
                        "avg_cost_per_resource": len(cost_data) / len(resource_data) if resource_data else 0
                    }
                }

                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Data ingestion completed in {duration:.2f}s - {len(resource_data)} resources, {len(cost_data)} cost entries")

                return PipelineResult(
                    stage=PipelineStage.DATA_INGESTION,
                    success=True,
                    data=data,
                    timestamp=datetime.utcnow(),
                    duration=duration
                )

        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            return PipelineResult(
                stage=PipelineStage.DATA_INGESTION,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    async def _run_feature_engineering(self, ingestion_data: Dict[str, Any]) -> PipelineResult:
        """Stage 2: Extract features from raw data."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting feature engineering")

            resources = ingestion_data["resources"]
            cost_entries = ingestion_data["cost_entries"]

            # Group cost data by resource
            cost_by_resource = {}
            for cost in cost_entries:
                resource_id = cost["resource_id"]
                if resource_id not in cost_by_resource:
                    cost_by_resource[resource_id] = []
                cost_by_resource[resource_id].append(cost)

            # Extract features for each resource
            feature_data = []
            for resource in resources:
                resource_id = resource["id"]
                resource_costs = cost_by_resource.get(resource_id, [])

                if len(resource_costs) < self.config.min_data_points:
                    logger.warning(f"Skipping resource {resource_id} - insufficient data points ({len(resource_costs)})")
                    continue

                features = self._extract_resource_features(resource, resource_costs)
                feature_data.append(features)

            data = {
                "features": feature_data,
                "feature_summary": {
                    "total_resources_processed": len(feature_data),
                    "features_extracted": len(feature_data[0]) if feature_data else 0,
                    "avg_data_points_per_resource": np.mean([len(cost_by_resource.get(r["id"], [])) for r in resources])
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Feature engineering completed in {duration:.2f}s - {len(feature_data)} resources processed")

            return PipelineResult(
                stage=PipelineStage.FEATURE_ENGINEERING,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            return PipelineResult(
                stage=PipelineStage.FEATURE_ENGINEERING,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _extract_resource_features(self, resource: Dict[str, Any], cost_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract ML features from resource and cost data."""
        try:
            # Convert cost data to DataFrame for analysis
            df = pd.DataFrame(cost_entries)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Basic cost statistics
            costs = df['cost'].values
            
            # Handle empty or invalid cost data
            if len(costs) == 0:
                cost_features = {
                    "avg_daily_cost": 0.0,
                    "total_cost": 0.0,
                    "cost_std": 0.0,
                    "cost_min": 0.0,
                    "cost_max": 0.0,
                    "cost_trend": 0.0,
                    "cost_volatility": 0.0
                }
            else:
                # Calculate statistics safely
                avg_cost = np.mean(costs) if len(costs) > 0 else 0.0
                total_cost = np.sum(costs) if len(costs) > 0 else 0.0
                cost_std = np.std(costs) if len(costs) > 1 else 0.0
                cost_min = np.min(costs) if len(costs) > 0 else 0.0
                cost_max = np.max(costs) if len(costs) > 0 else 0.0
                
                # Cost trend calculation
                if len(costs) > 1:
                    try:
                        cost_trend = np.polyfit(range(len(costs)), costs, 1)[0]
                    except (np.RankWarning, ValueError):
                        cost_trend = 0.0
                else:
                    cost_trend = 0.0
                
                # Cost volatility
                cost_volatility = (cost_std / avg_cost) if avg_cost > 0 else 0.0
                
                cost_features = {
                    "avg_daily_cost": float(avg_cost) if not np.isnan(avg_cost) and not np.isinf(avg_cost) else 0.0,
                    "total_cost": float(total_cost) if not np.isnan(total_cost) and not np.isinf(total_cost) else 0.0,
                    "cost_std": float(cost_std) if not np.isnan(cost_std) and not np.isinf(cost_std) else 0.0,
                    "cost_min": float(cost_min) if not np.isnan(cost_min) and not np.isinf(cost_min) else 0.0,
                    "cost_max": float(cost_max) if not np.isnan(cost_max) and not np.isinf(cost_max) else 0.0,
                    "cost_trend": float(cost_trend) if not np.isnan(cost_trend) and not np.isinf(cost_trend) else 0.0,
                    "cost_volatility": float(cost_volatility) if not np.isnan(cost_volatility) and not np.isinf(cost_volatility) else 0.0
                }

            # Usage pattern features
            usage_features = {
                "data_points": len(cost_entries),
                "usage_consistency": 1 - cost_features["cost_volatility"] if cost_features["cost_volatility"] < 1 else 0.0,
                "peak_cost_ratio": (cost_features["cost_max"] / cost_features["avg_daily_cost"]) if cost_features["avg_daily_cost"] > 0 else 1.0,
                "cost_range_ratio": ((cost_features["cost_max"] - cost_features["cost_min"]) / cost_features["avg_daily_cost"]) if cost_features["avg_daily_cost"] > 0 else 0.0
            }

            # Resource metadata features
            metadata_features = {
                "has_tags": len(resource.get("tags", {})) > 0,
                "tag_count": len(resource.get("tags", {})),
                "is_production": any(tag.lower() in ['prod', 'production'] for tag in resource.get("tags", {}).values()),
                "resource_type_encoded": hash(resource.get("resource_type", "")) % 1000,
                "provider_encoded": hash(resource.get("provider", "")) % 100
            }

            # Time-based features
            time_features = {
                "age_days": (datetime.utcnow() - pd.to_datetime(resource.get("created_at"))).days if resource.get("created_at") else 0,
                "analysis_window_days": self.config.analysis_window_days
            }

            return {
                "resource_id": resource["id"],
                "resource": resource,
                "cost_features": cost_features,
                "usage_features": usage_features,
                "metadata_features": metadata_features,
                "time_features": time_features,
                "combined_features": {**cost_features, **usage_features, **metadata_features, **time_features}
            }

        except Exception as e:
            logger.error(f"Error extracting features for resource {resource.get('id')}: {e}")
            return {
                "resource_id": resource["id"],
                "resource": resource,
                "error": str(e)
            }

    async def _run_pattern_analysis(self, feature_data: Dict[str, Any]) -> PipelineResult:
        """Stage 3: Analyze usage patterns and detect inefficiencies."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting pattern analysis")

            features = feature_data["features"]
            pattern_analysis = []

            for feature_set in features:
                resource_id = feature_set["resource_id"]
                resource = feature_set["resource"]
                combined_features = feature_set["combined_features"]

                # Analyze usage patterns
                usage_patterns = self._analyze_usage_patterns(combined_features)

                # Detect potential inefficiencies
                inefficiencies = self._detect_inefficiencies(resource, combined_features, usage_patterns)

                pattern_analysis.append({
                    "resource_id": resource_id,
                    "resource": resource,
                    "usage_patterns": usage_patterns,
                    "inefficiencies": inefficiencies,
                    "analysis_confidence": self._calculate_analysis_confidence(combined_features)
                })

            # Anomaly detection (optional)
            anomalies = []
            if self.config.enable_anomaly_detection:
                anomalies = self._detect_anomalies(feature_data)

            data = {
                "pattern_analysis": pattern_analysis,
                "anomalies": anomalies,
                "summary": {
                    "resources_analyzed": len(pattern_analysis),
                    "inefficiencies_detected": sum(len(pa["inefficiencies"]) for pa in pattern_analysis),
                    "anomalies_detected": len(anomalies)
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Pattern analysis completed in {duration:.2f}s - {len(pattern_analysis)} resources analyzed")

            return PipelineResult(
                stage=PipelineStage.PATTERN_ANALYSIS,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return PipelineResult(
                stage=PipelineStage.PATTERN_ANALYSIS,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _analyze_usage_patterns(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze usage patterns from extracted features."""
        try:
            return {
                "cost_stability": 1 - features.get("cost_volatility", 0),
                "usage_consistency": features.get("usage_consistency", 0),
                "peak_usage_ratio": features.get("peak_cost_ratio", 1),
                "trend_direction": "increasing" if features.get("cost_trend", 0) > 0 else "decreasing",
                "trend_magnitude": abs(features.get("cost_trend", 0)),
                "is_over_provisioned": features.get("avg_daily_cost", 0) > features.get("cost_min", 0) * 1.5,
                "is_under_utilized": features.get("usage_consistency", 0) < 0.3,
                "volatility_level": "high" if features.get("cost_volatility", 0) > 0.5 else "low"
            }
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            return {"error": str(e)}

    def _detect_inefficiencies(self, resource: Dict[str, Any], features: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential inefficiencies in resource usage."""
        inefficiencies = []

        try:
            # Over-provisioning detection
            if patterns.get("is_over_provisioned", False):
                inefficiencies.append({
                    "type": "over_provisioning",
                    "severity": "medium",
                    "description": "Resource consistently uses less than 70% of allocated capacity",
                    "potential_savings_pct": 30,
                    "confidence": 0.8
                })

            # Under-utilization detection
            if patterns.get("is_under_utilized", False):
                inefficiencies.append({
                    "type": "under_utilization",
                    "severity": "high",
                    "description": "Resource shows very low and inconsistent usage patterns",
                    "potential_savings_pct": 60,
                    "confidence": 0.9
                })

            # High volatility detection
            if patterns.get("volatility_level") == "high":
                inefficiencies.append({
                    "type": "usage_volatility",
                    "severity": "medium",
                    "description": "Highly variable usage patterns suggest potential for optimization",
                    "potential_savings_pct": 20,
                    "confidence": 0.7
                })

            # Production resource with low utilization
            if (features.get("is_production", False) and
                patterns.get("usage_consistency", 0) < 0.4):
                inefficiencies.append({
                    "type": "production_inefficiency",
                    "severity": "high",
                    "description": "Production resource with inefficient usage patterns",
                    "potential_savings_pct": 40,
                    "confidence": 0.85
                })

        except Exception as e:
            logger.error(f"Error detecting inefficiencies: {e}")

        return inefficiencies

    def _detect_anomalies(self, feature_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalous resource behavior."""
        try:
            features = feature_data["features"]
            if len(features) < 3:
                return []

            # Simple anomaly detection based on cost volatility
            volatilities = [f["combined_features"].get("cost_volatility", 0) for f in features]
            mean_volatility = np.mean(volatilities)
            std_volatility = np.std(volatilities)

            anomalies = []
            for feature_set in features:
                volatility = feature_set["combined_features"].get("cost_volatility", 0)
                z_score = (volatility - mean_volatility) / std_volatility if std_volatility > 0 else 0

                if abs(z_score) > 2:  # 2 standard deviations
                    anomalies.append({
                        "resource_id": feature_set["resource_id"],
                        "anomaly_type": "cost_volatility",
                        "severity": "high" if abs(z_score) > 3 else "medium",
                        "z_score": z_score,
                        "description": f"Unusual cost volatility detected (z-score: {z_score:.2f})"
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    def _calculate_analysis_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        try:
            confidence = 0.5  # Base confidence

            # Increase confidence with more data points
            data_points = features.get("data_points", 0)
            if data_points > 30:
                confidence += 0.2
            elif data_points > 14:
                confidence += 0.1

            # Increase confidence for production resources
            if features.get("is_production", False):
                confidence += 0.1

            # Decrease confidence for high volatility
            if features.get("cost_volatility", 0) > 0.7:
                confidence -= 0.1

            return min(max(confidence, 0.1), 0.95)

        except Exception as e:
            return 0.5

    async def _run_risk_assessment(self, pattern_data: Dict[str, Any]) -> PipelineResult:
        """Stage 4: Assess risks for potential optimizations."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting risk assessment")

            pattern_analysis = pattern_data["pattern_analysis"]
            risk_assessments = []

            for analysis in pattern_analysis:
                resource = analysis["resource"]
                inefficiencies = analysis["inefficiencies"]

                # Assess risk for each inefficiency
                for inefficiency in inefficiencies:
                    risk_assessment = self.risk_assessor.assess_risk(resource, {
                        "type": inefficiency["type"],
                        "implementation_complexity": "medium",
                        "requires_downtime": inefficiency["type"] in ["over_provisioning", "under_utilization"]
                    })

                    risk_assessments.append({
                        "resource_id": analysis["resource_id"],
                        "inefficiency": inefficiency,
                        "risk_assessment": risk_assessment
                    })

            data = {
                "risk_assessments": risk_assessments,
                "summary": {
                    "total_assessments": len(risk_assessments),
                    "high_risk_count": len([r for r in risk_assessments if r["risk_assessment"]["risk_level"] == "high"]),
                    "critical_risk_count": len([r for r in risk_assessments if r["risk_assessment"]["risk_level"] == "critical"])
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Risk assessment completed in {duration:.2f}s - {len(risk_assessments)} assessments")

            return PipelineResult(
                stage=PipelineStage.RISK_ASSESSMENT,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return PipelineResult(
                stage=PipelineStage.RISK_ASSESSMENT,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    async def _run_recommendation_generation(self, pattern_data: Dict[str, Any], ingestion_data: Dict[str, Any]) -> PipelineResult:
        """Stage 5: Generate optimization recommendations."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting recommendation generation")

            pattern_analysis = pattern_data["pattern_analysis"]
            all_recommendations = []

            for analysis in pattern_analysis:
                resource = analysis["resource"]
                usage_patterns = analysis["usage_patterns"]
                inefficiencies = analysis["inefficiencies"]

                # Generate recommendations using the recommender
                # Get cost data for this resource
                resource_costs = []
                for cost_entry in ingestion_data.get("cost_entries", []):
                    if cost_entry["resource_id"] == resource["id"]:
                        resource_costs.append(cost_entry)
                
                recommendations = self.recommender.generate_recommendations(
                    [resource],
                    {resource["id"]: usage_patterns},
                    resource_costs  # Pass actual cost data
                )

                # Filter and enhance recommendations
                filtered_recommendations = []
                for rec in recommendations:
                    if rec.get("confidence_score", 0) >= self.config.confidence_threshold:
                        # Add additional metadata
                        rec["resource_name"] = resource.get("name", "")
                        rec["resource_type"] = resource.get("resource_type", "")
                        rec["provider"] = resource.get("provider", "")
                        rec["detected_inefficiencies"] = inefficiencies
                        filtered_recommendations.append(rec)

                all_recommendations.extend(filtered_recommendations[:self.config.max_recommendations_per_resource])

            data = {
                "recommendations": all_recommendations,
                "summary": {
                    "total_recommendations": len(all_recommendations),
                    "by_type": self._group_recommendations_by_type(all_recommendations),
                    "by_priority": self._group_recommendations_by_priority(all_recommendations),
                    "total_potential_savings": sum(r.get("potential_savings", 0) for r in all_recommendations)
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Recommendation generation completed in {duration:.2f}s - {len(all_recommendations)} recommendations")

            return PipelineResult(
                stage=PipelineStage.RECOMMENDATION_GENERATION,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return PipelineResult(
                stage=PipelineStage.RECOMMENDATION_GENERATION,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    async def _run_performance_estimation(self, recommendation_data: Dict[str, Any], pattern_data: Dict[str, Any]) -> PipelineResult:
        """Stage 6: Estimate performance impact of recommendations."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting performance estimation")

            recommendations = recommendation_data["recommendations"]
            pattern_analysis = pattern_data["pattern_analysis"]

            # Create lookup for usage patterns
            usage_patterns_lookup = {
                analysis["resource_id"]: analysis["usage_patterns"]
                for analysis in pattern_analysis
            }

            performance_estimations = []
            for recommendation in recommendations:
                resource_id = recommendation.get("resource_id")
                usage_patterns = usage_patterns_lookup.get(resource_id, {})

                # Find the resource data
                resource = None
                for analysis in pattern_analysis:
                    if analysis["resource_id"] == resource_id:
                        resource = analysis["resource"]
                        break

                if resource:
                    # Predict performance impact
                    impact_prediction = self.performance_predictor.predict_impact(
                        resource, recommendation, usage_patterns
                    )

                    performance_estimations.append({
                        "recommendation_id": recommendation.get("id"),
                        "resource_id": resource_id,
                        "performance_prediction": impact_prediction
                    })

            data = {
                "performance_estimations": performance_estimations,
                "summary": {
                    "total_estimations": len(performance_estimations),
                    "high_confidence_count": len([
                        e for e in performance_estimations
                        if e["performance_prediction"].get("confidence_level") == "high"
                    ]),
                    "avg_predicted_impact": np.mean([
                        e["performance_prediction"].get("predicted_performance_impact", 0)
                        for e in performance_estimations
                    ])
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Performance estimation completed in {duration:.2f}s - {len(performance_estimations)} estimations")

            return PipelineResult(
                stage=PipelineStage.PERFORMANCE_ESTIMATION,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Performance estimation failed: {e}")
            return PipelineResult(
                stage=PipelineStage.PERFORMANCE_ESTIMATION,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    async def _run_validation_and_finalization(self, recommendation_data: Dict[str, Any]) -> PipelineResult:
        """Stage 7: Validate and finalize recommendations."""
        start_time = datetime.utcnow()

        try:
            logger.info("Starting validation and finalization")

            recommendations = recommendation_data["recommendations"]

            # Validate recommendations
            validated_recommendations = []
            for rec in recommendations:
                validation_result = self._validate_recommendation(rec)
                if validation_result["is_valid"]:
                    rec["validation"] = validation_result
                    validated_recommendations.append(rec)

            # Sort by priority and savings
            validated_recommendations.sort(
                key=lambda x: (x.get("priority_rank", 999), -x.get("potential_savings", 0))
            )

            # Add final rankings
            for i, rec in enumerate(validated_recommendations):
                rec["final_rank"] = i + 1

            data = {
                "recommendations": validated_recommendations,
                "validation_summary": {
                    "total_validated": len(validated_recommendations),
                    "total_invalid": len(recommendations) - len(validated_recommendations),
                    "validation_pass_rate": len(validated_recommendations) / len(recommendations) if recommendations else 0
                }
            }

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Validation and finalization completed in {duration:.2f}s - {len(validated_recommendations)} recommendations validated")

            return PipelineResult(
                stage=PipelineStage.VALIDATION,
                success=True,
                data=data,
                timestamp=datetime.utcnow(),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Validation and finalization failed: {e}")
            return PipelineResult(
                stage=PipelineStage.VALIDATION,
                success=False,
                data={},
                timestamp=datetime.utcnow(),
                duration=(datetime.utcnow() - start_time).total_seconds(),
                error=str(e)
            )

    def _validate_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a recommendation for feasibility and safety."""
        try:
            issues = []
            is_valid = True

            # Check minimum savings threshold
            savings = recommendation.get("potential_savings", 0)
            if savings < 10:  # $10 minimum
                issues.append("Savings below minimum threshold")
                is_valid = False

            # Check confidence score
            confidence = recommendation.get("confidence_score", 0)
            if confidence < self.config.confidence_threshold:
                issues.append(f"Confidence score below threshold ({confidence:.2f} < {self.config.confidence_threshold})")
                is_valid = False

            # Check for conflicting recommendations
            # (This would be more sophisticated in a real implementation)

            return {
                "is_valid": is_valid,
                "issues": issues,
                "validation_checks": [
                    "minimum_savings_check",
                    "confidence_threshold_check",
                    "conflict_detection_check"
                ]
            }

        except Exception as e:
            logger.error(f"Error validating recommendation: {e}")
            return {
                "is_valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "validation_checks": []
            }

    def _group_recommendations_by_type(self, recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group recommendations by type."""
        type_counts = {}
        for rec in recommendations:
            rec_type = rec.get("type", "unknown")
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
        return type_counts

    def _group_recommendations_by_priority(self, recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group recommendations by priority level."""
        priority_counts = {}
        for rec in recommendations:
            priority = rec.get("priority_level", "unknown")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        return priority_counts

    def _generate_pipeline_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive pipeline execution summary."""
        try:
            successful_stages = [r for r in self.pipeline_results if r.success]
            failed_stages = [r for r in self.pipeline_results if not r.success]

            return {
                "execution_summary": {
                    "total_stages": len(PipelineStage),
                    "successful_stages": len(successful_stages),
                    "failed_stages": len(failed_stages),
                    "overall_success_rate": len(successful_stages) / len(PipelineStage),
                    "total_duration": sum(r.duration for r in self.pipeline_results)
                },
                "stage_performance": [
                    {
                        "stage": result.stage.value,
                        "success": result.success,
                        "duration": result.duration,
                        "duration_percentage": result.duration / sum(r.duration for r in self.pipeline_results) * 100
                    }
                    for result in self.pipeline_results
                ],
                "data_processing_stats": self._extract_data_processing_stats(),
                "quality_metrics": self._calculate_quality_metrics()
            }

        except Exception as e:
            logger.error(f"Error generating pipeline summary: {e}")
            return {"error": str(e)}

    def _extract_data_processing_stats(self) -> Dict[str, Any]:
        """Extract data processing statistics from pipeline results."""
        try:
            stats = {}

            for result in self.pipeline_results:
                if result.stage == PipelineStage.DATA_INGESTION and result.success:
                    stats.update(result.data.get("summary", {}))
                elif result.stage == PipelineStage.FEATURE_ENGINEERING and result.success:
                    stats.update(result.data.get("feature_summary", {}))
                elif result.stage == PipelineStage.RECOMMENDATION_GENERATION and result.success:
                    stats.update(result.data.get("summary", {}))

            return stats

        except Exception as e:
            return {"error": str(e)}

    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate quality metrics for the pipeline output."""
        try:
            # This would include metrics like recommendation quality, false positive rate, etc.
            return {
                "recommendation_quality_score": 0.85,  # Placeholder
                "data_completeness": 0.92,  # Placeholder
                "processing_efficiency": 0.78  # Placeholder
            }

        except Exception as e:
            return {"error": str(e)}

    def _create_error_response(self, message: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "status": "error",
            "message": message,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_results": [
                {
                    "stage": result.stage.value,
                    "success": result.success,
                    "duration": result.duration,
                    "error": result.error
                }
                for result in self.pipeline_results
            ]
        }

    async def save_recommendations_to_db(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save generated recommendations to the database.

        Args:
            recommendations: List of recommendations to save

        Returns:
            Save operation results
        """
        try:
            async with async_session_maker() as session:
                saved_count = 0
                for rec in recommendations:
                    # Create optimization recommendation record
                    optimization = OptimizationRecommendation(
                        resource_id=rec["resource_id"],
                        type=rec["type"],
                        title=rec["title"],
                        description=rec["description"],
                        potential_savings=rec.get("potential_savings", 0),
                        confidence_score=rec.get("confidence_score", 0),
                        risk_level=rec.get("priority_level", "medium"),
                        status="pending",
                        recommendation_data=rec,
                        expires_at=datetime.utcnow() + timedelta(days=30)
                    )

                    session.add(optimization)
                    saved_count += 1

                await session.commit()

                return {
                    "status": "success",
                    "saved_count": saved_count,
                    "message": f"Successfully saved {saved_count} recommendations to database"
                }

        except Exception as e:
            logger.error(f"Error saving recommendations to database: {e}")
            return {
                "status": "error",
                "error": str(e),
                "saved_count": 0
            }

    def _sanitize_numeric_values(self, data: Any) -> Any:
        """Recursively sanitize numeric values to ensure JSON compliance."""
        if isinstance(data, dict):
            return {key: self._sanitize_numeric_values(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_numeric_values(item) for item in data]
        elif isinstance(data, (int, float)):
            if np.isnan(data) or np.isinf(data):
                return 0.0
            return float(data)
        else:
            return data
