from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class CloudResource(Base):
    """Cloud resource inventory table"""
    __tablename__ = "cloud_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), nullable=False)  # aws, gcp, azure
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)  # ec2, rds, gcs, etc.
    name = Column(String(255))
    region = Column(String(50))
    tags = Column(JSON, default={})
    specifications = Column(JSON, default={})  # instance type, storage size, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cost_entries = relationship("CostEntry", back_populates="resource")
    optimization_recommendations = relationship("OptimizationRecommendation", back_populates="resource")

class CostEntry(Base):
    """Cost data time series table"""
    __tablename__ = "cost_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("cloud_resources.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    usage_quantity = Column(Float)
    usage_unit = Column(String(50))  # hours, GB, requests, etc.
    service_name = Column(String(100))
    cost_category = Column(String(50))  # compute, storage, network, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = relationship("CloudResource", back_populates="cost_entries")

class OptimizationRecommendation(Base):
    """AI-generated optimization recommendations"""
    __tablename__ = "optimization_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("cloud_resources.id"), nullable=False)
    type = Column(String(50), nullable=False)  # rightsizing, reserved_instance, spot_instance
    title = Column(String(255), nullable=False)
    description = Column(Text)
    potential_savings = Column(Float)  # monthly savings estimate
    confidence_score = Column(Float)  # 0.0 to 1.0
    risk_level = Column(String(20))  # low, medium, high
    status = Column(String(20), default='pending')  # pending, approved, executed, rejected
    recommendation_data = Column(JSON)  # specific optimization parameters
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    resource = relationship("CloudResource", back_populates="optimization_recommendations")
    executions = relationship("OptimizationExecution", back_populates="recommendation")

class OptimizationExecution(Base):
    """Track execution of optimization recommendations"""
    __tablename__ = "optimization_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("optimization_recommendations.id"), nullable=False)
    status = Column(String(20), nullable=False)  # executing, completed, failed, rolled_back
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_details = Column(JSON)  # logs, errors, rollback info
    actual_savings = Column(Float)  # measured post-execution
    
    # Relationships
    recommendation = relationship("OptimizationRecommendation", back_populates="executions")

class User(Base):
    """User management table"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(255))
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
