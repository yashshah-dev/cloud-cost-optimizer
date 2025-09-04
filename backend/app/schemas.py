from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from enum import Enum
import uuid

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

class ResourceType(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    OTHER = "other"

class OptimizationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Request schemas
class CostSummaryRequest(BaseModel):
    start_date: date = Field(..., description="Start date for cost summary")
    end_date: date = Field(..., description="End date for cost summary")
    providers: Optional[List[CloudProvider]] = None
    group_by: Optional[str] = Field(None, description="Group by provider, service, or resource")

class ResourceUsageRequest(BaseModel):
    resource_id: str = Field(..., description="Resource ID")
    start_date: date
    end_date: date
    metrics: Optional[List[str]] = None

class OptimizationRequest(BaseModel):
    resource_ids: Optional[List[str]] = None
    resource_types: Optional[List[ResourceType]] = None
    providers: Optional[List[CloudProvider]] = None
    min_savings: Optional[float] = Field(None, ge=0, description="Minimum monthly savings threshold")

# Response schemas
class CloudResourceResponse(BaseModel):
    id: str
    provider: CloudProvider
    resource_id: str
    resource_type: ResourceType
    name: Optional[str]
    region: str
    tags: Dict[str, str] = {}
    specifications: Dict[str, Any] = {}
    monthly_cost: Optional[float] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class CostEntryResponse(BaseModel):
    id: str
    resource_id: str
    date: date
    cost: float
    currency: str = "USD"
    usage_quantity: Optional[float]
    usage_unit: Optional[str]
    service_name: str
    cost_category: str

class CostSummaryResponse(BaseModel):
    total_cost: float
    currency: str = "USD"
    period_start: date
    period_end: date
    cost_by_provider: Dict[str, float] = {}
    cost_by_service: Dict[str, float] = {}
    cost_by_category: Dict[str, float] = {}
    daily_costs: List[Dict[str, Any]] = []
    top_resources: List[CloudResourceResponse] = []

class UsageMetricsResponse(BaseModel):
    resource_id: str
    period_start: date
    period_end: date
    metrics: Dict[str, List[Dict[str, Any]]] = {}
    utilization_summary: Dict[str, float] = {}

class OptimizationRecommendationResponse(BaseModel):
    id: str
    resource_id: str
    resource: Optional[CloudResourceResponse]
    type: str
    title: str
    description: str
    potential_savings: float
    confidence_score: float
    risk_level: RiskLevel
    status: OptimizationStatus
    recommendation_data: Dict[str, Any] = {}
    created_at: datetime
    expires_at: Optional[datetime]

class OptimizationsResponse(BaseModel):
    total_count: int
    total_potential_savings: float
    recommendations: List[OptimizationRecommendationResponse]
    summary_by_type: Dict[str, int] = {}
    summary_by_risk: Dict[str, int] = {}

class ExplainOptimizationRequest(BaseModel):
    optimization_id: str = Field(..., description="UUID of the optimization recommendation")
    resource_id: str = Field(..., description="UUID of the cloud resource")

# Agent-related schemas
class AgentQuery(BaseModel):
    query: str = Field(..., description="Natural language query about costs or optimizations")
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    response: str
    recommendations: List[OptimizationRecommendationResponse] = []
    data: Optional[Dict[str, Any]] = None
    confidence: float = Field(ge=0, le=1)

# Error schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

# Health check
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database: bool
    redis: bool
    providers: Dict[str, bool] = {}

# Authentication schemas
class UserLogin(BaseModel):
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
