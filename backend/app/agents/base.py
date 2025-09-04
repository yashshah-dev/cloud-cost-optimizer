from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentMessage:
    """Represents a message in agent conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentContext:
    """Context for agent operations"""
    user_id: str
    session_id: str
    conversation_history: List[AgentMessage]
    current_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class BaseTool(ABC):
    """Base class for agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Any:
        pass

class BaseAgent(ABC):
    """Base class for AI agents"""
    
    def __init__(self, name: str, description: str, tools: List[BaseTool] = None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.memory = {}
    
    @abstractmethod
    async def process_query(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Process a user query and return response"""
        pass
    
    @abstractmethod
    async def analyze_data(self, data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Analyze data and provide insights"""
        pass
    
    def add_tool(self, tool: BaseTool):
        """Add a tool to the agent"""
        self.tools.append(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return next((tool for tool in self.tools if tool.name == name), None)
    
    def update_memory(self, key: str, value: Any):
        """Update agent memory"""
        self.memory[key] = value
    
    def get_memory(self, key: str) -> Any:
        """Get value from agent memory"""
        return self.memory.get(key)
