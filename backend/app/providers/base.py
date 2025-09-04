from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel
from enum import Enum

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

class ResourceType(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    OTHER = "other"

class CloudResourceDTO(BaseModel):
    """Unified resource representation across cloud providers"""
    provider: CloudProvider
    resource_id: str
    resource_type: ResourceType
    name: Optional[str] = None
    region: str
    tags: Dict[str, str] = {}
    specifications: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

class CostEntryDTO(BaseModel):
    """Unified cost entry representation"""
    resource_id: str
    date: date
    cost: float
    currency: str = "USD"
    usage_quantity: Optional[float] = None
    usage_unit: Optional[str] = None
    service_name: str
    cost_category: str

class CloudProviderClient(ABC):
    """Abstract base class for cloud provider clients"""
    
    def __init__(self, provider: CloudProvider):
        self.provider = provider
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the cloud provider"""
        pass
    
    @abstractmethod
    async def get_resources(self, resource_types: Optional[List[ResourceType]] = None, 
                          region: Optional[str] = None) -> List[CloudResourceDTO]:
        """Get cloud resources inventory"""
        pass
    
    @abstractmethod
    async def get_cost_data(self, start_date: date, end_date: date, 
                          resource_ids: Optional[List[str]] = None) -> List[CostEntryDTO]:
        """Get cost data for specified date range"""
        pass
    
    @abstractmethod
    async def get_usage_metrics(self, resource_id: str, start_date: date, 
                              end_date: date) -> Dict[str, Any]:
        """Get detailed usage metrics for a resource"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate that credentials are working"""
        pass
    
    def is_authenticated(self) -> bool:
        return self._authenticated
