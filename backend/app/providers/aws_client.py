import boto3
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from botocore.exceptions import ClientError, NoCredentialsError

from .base import CloudProviderClient, CloudProvider, ResourceType, CloudResourceDTO, CostEntryDTO

logger = structlog.get_logger()

class AWSClient(CloudProviderClient):
    """AWS cloud provider implementation"""
    
    def __init__(self, access_key_id: str, secret_access_key: str, region: str = "us-east-1"):
        super().__init__(CloudProvider.AWS)
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        self.session = None
        self.cost_explorer = None
        self.ec2_client = None
        self.cloudwatch = None
    
    async def authenticate(self) -> bool:
        """Initialize AWS session and clients"""
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
            
            # Initialize clients
            self.cost_explorer = self.session.client('ce')
            self.ec2_client = self.session.client('ec2')
            self.cloudwatch = self.session.client('cloudwatch')
            
            # Test authentication
            if await self.validate_credentials():
                self._authenticated = True
                logger.info("AWS authentication successful", region=self.region)
                return True
            
        except Exception as e:
            logger.error("AWS authentication failed", error=str(e))
            return False
        
        return False
    
    async def validate_credentials(self) -> bool:
        """Validate AWS credentials by making a simple API call"""
        try:
            # Use Cost Explorer to validate (async wrapper)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._validate_cost_explorer)
            return True
        except Exception as e:
            logger.error("AWS credential validation failed", error=str(e))
            return False
    
    def _validate_cost_explorer(self):
        """Synchronous validation call"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=1)
        
        self.cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.isoformat(),
                'End': end_date.isoformat()
            },
            Granularity='DAILY',
            Metrics=['BlendedCost']
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_resources(self, resource_types: Optional[List[ResourceType]] = None,
                          region: Optional[str] = None) -> List[CloudResourceDTO]:
        """Get AWS resources inventory"""
        if not self._authenticated:
            raise RuntimeError("Not authenticated with AWS")
        
        resources = []
        target_region = region or self.region
        
        # Get EC2 instances
        if not resource_types or ResourceType.COMPUTE in resource_types:
            ec2_resources = await self._get_ec2_instances(target_region)
            resources.extend(ec2_resources)
        
        # Add more resource types as needed (RDS, S3, etc.)
        
        logger.info("Retrieved AWS resources", count=len(resources), region=target_region)
        return resources
    
    async def _get_ec2_instances(self, region: str) -> List[CloudResourceDTO]:
        """Get EC2 instances"""
        loop = asyncio.get_event_loop()
        instances = await loop.run_in_executor(None, self._fetch_ec2_instances, region)
        
        resources = []
        for instance in instances:
            # Extract tags
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            
            # Extract specifications
            specs = {
                'instance_type': instance['InstanceType'],
                'state': instance['State']['Name'],
                'vpc_id': instance.get('VpcId'),
                'subnet_id': instance.get('SubnetId'),
                'ami_id': instance['ImageId'],
                'platform': instance.get('Platform', 'linux')
            }
            
            resource = CloudResourceDTO(
                provider=CloudProvider.AWS,
                resource_id=instance['InstanceId'],
                resource_type=ResourceType.COMPUTE,
                name=tags.get('Name', instance['InstanceId']),
                region=region,
                tags=tags,
                specifications=specs,
                created_at=instance['LaunchTime'] if 'LaunchTime' in instance else None
            )
            resources.append(resource)
        
        return resources
    
    def _fetch_ec2_instances(self, region: str) -> List[Dict[str, Any]]:
        """Synchronous EC2 instance fetch"""
        ec2 = self.session.client('ec2', region_name=region)
        
        paginator = ec2.get_paginator('describe_instances')
        instances = []
        
        for page in paginator.paginate():
            for reservation in page['Reservations']:
                instances.extend(reservation['Instances'])
        
        return instances
    
    async def get_cost_data(self, start_date: date, end_date: date,
                          resource_ids: Optional[List[str]] = None) -> List[CostEntryDTO]:
        """Get AWS cost data using Cost Explorer"""
        if not self._authenticated:
            raise RuntimeError("Not authenticated with AWS")
        
        loop = asyncio.get_event_loop()
        cost_data = await loop.run_in_executor(
            None, self._fetch_cost_data, start_date, end_date, resource_ids
        )
        
        cost_entries = []
        
        for item in cost_data:
            # Parse AWS Cost Explorer response
            for time_period in item['TimePeriod']:
                cost_entry = CostEntryDTO(
                    resource_id=item.get('ResourceId', 'unknown'),
                    date=datetime.strptime(time_period['Start'], '%Y-%m-%d').date(),
                    cost=float(item['Amount']),
                    service_name=item.get('Service', 'AWS'),
                    cost_category=self._map_aws_service_to_category(item.get('Service', ''))
                )
                cost_entries.append(cost_entry)
        
        logger.info("Retrieved AWS cost data", 
                   start_date=start_date, end_date=end_date, 
                   entries=len(cost_entries))
        return cost_entries
    
    def _fetch_cost_data(self, start_date: date, end_date: date, 
                        resource_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Synchronous cost data fetch"""
        response = self.cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.isoformat(),
                'End': end_date.isoformat()
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
            ]
        )
        
        return response.get('ResultsByTime', [])
    
    async def get_usage_metrics(self, resource_id: str, start_date: date,
                              end_date: date) -> Dict[str, Any]:
        """Get CloudWatch metrics for a resource"""
        if not self._authenticated:
            raise RuntimeError("Not authenticated with AWS")
        
        # Implementation depends on resource type
        # For now, return basic EC2 metrics
        loop = asyncio.get_event_loop()
        metrics = await loop.run_in_executor(
            None, self._fetch_cloudwatch_metrics, resource_id, start_date, end_date
        )
        
        return metrics
    
    def _fetch_cloudwatch_metrics(self, resource_id: str, start_date: date,
                                 end_date: date) -> Dict[str, Any]:
        """Fetch CloudWatch metrics for EC2 instance"""
        try:
            # Get CPU utilization
            cpu_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': resource_id}
                ],
                StartTime=datetime.combine(start_date, datetime.min.time()),
                EndTime=datetime.combine(end_date, datetime.max.time()),
                Period=3600,  # 1 hour
                Statistics=['Average', 'Maximum']
            )
            
            metrics = {
                'cpu_utilization': [
                    {
                        'timestamp': point['Timestamp'],
                        'average': point['Average'],
                        'maximum': point['Maximum']
                    }
                    for point in cpu_response['Datapoints']
                ]
            }
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to fetch CloudWatch metrics", 
                        resource_id=resource_id, error=str(e))
            return {}
    
    def _map_aws_service_to_category(self, service: str) -> str:
        """Map AWS service names to cost categories"""
        service_mapping = {
            'Amazon Elastic Compute Cloud - Compute': 'compute',
            'Amazon Elastic Block Store': 'storage',
            'Amazon Simple Storage Service': 'storage',
            'Amazon Relational Database Service': 'database',
            'Amazon Virtual Private Cloud': 'network',
        }
        
        for key, category in service_mapping.items():
            if key in service:
                return category
        
        return 'other'
