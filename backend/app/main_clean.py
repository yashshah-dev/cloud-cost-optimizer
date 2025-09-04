from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc, and_, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import time
import uuid
import os
import json

# Import models and schemas
from .database import get_db, engine
from .models.database import (
    CloudResource, OptimizationRecommendation, CostEntry, UsageMetric, 
    PerformanceMetric, AlertRule, Alert
)
from .schemas import (
    OptimizationRequest, OptimizationsResponse, OptimizationRecommendationResponse,
    CloudResourceResponse, ExplainOptimizationRequest, AgentQuery, AgentResponse, 
    HealthResponse, ErrorResponse, CostSummaryResponse, UsageMetricsResponse,
    CostEntryResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cloud Cost Optimizer API",
    description="AI-powered cloud cost optimization platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"[{request_id}] --> {request.method} {request.url.path}")
    logger.info(f"[{request_id}] Headers: {dict(request.headers)}")
    
    # Get request body for POST requests
    if request.method == "POST":
        body = await request.body()
        if body:
            try:
                body_str = body.decode('utf-8')
                logger.info(f"[{request_id}] Request Body: {body_str}")
            except UnicodeDecodeError:
                logger.info(f"[{request_id}] Request Body: <binary data>")
    
    # Create a new request object with the body
    async def receive():
        return {"type": "http.request", "body": body if request.method == "POST" else b""}
    
    request._receive = receive
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"[{request_id}] <-- {response.status_code} ({process_time:.3f}s)")
    logger.info(f"[{request_id}] Response Headers: {dict(response.headers)}")
    
    return response

# Authentication (placeholder for development)
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
):
    """Placeholder for authentication - will be implemented in Phase 2"""
    # For development, allow unauthenticated requests
    return {"id": "user-1", "email": "demo@example.com"}

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    start_time = time.time()

    try:
        # Test database connection
        logger.info("Testing database connection...")
        await db.execute(select(1))
        db_status = True
        logger.info("Database connection test passed")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = False
    
    response_time = time.time() - start_time
    logger.info(f"Health check completed in {response_time:.3f}s - Status: {'healthy' if db_status else 'unhealthy'}")
    
    return HealthResponse(
        status="healthy" if db_status else "unhealthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database=db_status,
        redis=False,  # Redis check can be added later
        providers={"aws": True, "gcp": False, "azure": False}
    )

# Optimizations endpoint (working)
@app.post("/api/v1/optimizations", response_model=OptimizationsResponse)
async def get_optimizations(
    db: AsyncSession = Depends(get_db)
):
    """Get optimization recommendations"""
    logger.info("Optimizations endpoint called")
    start_time = time.time()
    
    try:
        # Query all optimization recommendations
        logger.info("Querying optimization recommendations from database...")
        query = select(OptimizationRecommendation).order_by(desc(OptimizationRecommendation.potential_savings))
        result = await db.execute(query)
        recommendations = result.scalars().all()
        logger.info(f"Found {len(recommendations)} optimization recommendations")
        
        # Convert to response format
        recommendation_responses = []
        for i, rec in enumerate(recommendations):
            logger.info(f"Processing recommendation {i+1}/{len(recommendations)}: {rec.id}")
            
            # Get resource details
            resource_query = select(CloudResource).where(CloudResource.id == rec.resource_id)
            resource_result = await db.execute(resource_query)
            resource = resource_result.scalar_one_or_none()
            
            resource_response = None
            if resource:
                resource_response = CloudResourceResponse(
                    id=str(resource.id),
                    provider=resource.provider,
                    resource_id=resource.resource_id,
                    resource_type=resource.resource_type,
                    name=resource.name,
                    region=resource.region,
                    tags=resource.tags or {},
                    specifications=resource.specifications or {},
                    monthly_cost=None,  # Will be calculated from cost_entries if needed
                    created_at=resource.created_at,
                    updated_at=resource.updated_at
                )
            
            recommendation_responses.append(OptimizationRecommendationResponse(
                id=str(rec.id),
                resource_id=str(rec.resource_id),
                resource=resource_response,
                type=rec.type,
                title=rec.title,
                description=rec.description,
                potential_savings=rec.potential_savings,
                confidence_score=rec.confidence_score,
                risk_level=rec.risk_level,
                status=rec.status,
                recommendation_data=rec.recommendation_data or {},
                created_at=rec.created_at,
                expires_at=rec.expires_at
            ))
        
        # Calculate summaries
        total_savings = sum(rec.potential_savings for rec in recommendations)
        
        summary_by_type = {}
        summary_by_risk = {}
        for rec in recommendations:
            summary_by_type[rec.type] = summary_by_type.get(rec.type, 0) + 1
            summary_by_risk[rec.risk_level] = summary_by_risk.get(rec.risk_level, 0) + 1
        
        response_time = time.time() - start_time
        logger.info(f"Optimizations endpoint completed in {response_time:.3f}s - Found {len(recommendation_responses)} recommendations, total savings: ${total_savings:.2f}")
        
        return OptimizationsResponse(
            total_count=len(recommendations),
            total_potential_savings=total_savings,
            recommendations=recommendation_responses,
            summary_by_type=summary_by_type,
            summary_by_risk=summary_by_risk
        )
    
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Error in optimizations endpoint after {response_time:.3f}s: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization recommendations"
        )

# Simple explain-optimization endpoint (working)
@app.post("/api/v1/agent/explain-optimization")
async def explain_optimization_with_llm(request: ExplainOptimizationRequest):
    """Generate natural language explanation for an optimization using local LLM."""
    logger.info("=== EXPLAIN-OPTIMIZATION ENDPOINT CALLED ===")
    logger.info(f"Request: optimization_id={request.optimization_id}, resource_id={request.resource_id}")
    
    return {
        "explanation": "This optimization will help reduce your cloud costs by optimizing resource usage. Based on the analysis, implementing this change could result in significant monthly savings while maintaining performance.",
        "optimization_id": request.optimization_id,
        "resource_id": request.resource_id,
        "llm_available": False,
        "mock_data_used": True,
        "generated_at": datetime.utcnow().isoformat()
    }

# Resources endpoint
@app.get("/api/v1/resources", response_model=List[CloudResourceResponse])
async def get_resources(db: AsyncSession = Depends(get_db)):
    """Get all cloud resources"""
    logger.info("Resources endpoint called")
    start_time = time.time()
    
    try:
        query = select(CloudResource)
        result = await db.execute(query)
        resources = result.scalars().all()
        
        response_data = []
        for resource in resources:
            response_data.append(CloudResourceResponse(
                id=str(resource.id),
                provider=resource.provider,
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                name=resource.name,
                region=resource.region,
                tags=resource.tags or {},
                specifications=resource.specifications or {},
                monthly_cost=None,
                created_at=resource.created_at,
                updated_at=resource.updated_at
            ))
        
        response_time = time.time() - start_time
        logger.info(f"Resources endpoint completed in {response_time:.3f}s - Found {len(response_data)} resources")
        
        return response_data
    
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Error in resources endpoint after {response_time:.3f}s: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get resources"
        )

# Test endpoint for debugging
@app.post("/api/v1/test-simple")
async def test_simple():
    """Simple test endpoint"""
    logger.info("Simple test endpoint called")
    return {"status": "working", "message": "Simple endpoint works"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
