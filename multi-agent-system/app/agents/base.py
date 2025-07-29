from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from app.models.state import AgentState
from app.core.exceptions import AgentException

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self._execution_count = 0
        
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the state and return updated state"""
        pass
    
    def pre_process(self, state: AgentState) -> AgentState:
        """Pre-processing hook"""
        self._execution_count += 1
        state["agent_path"].append(self.name)
        self.logger.info(f"Starting {self.name} processing")
        return state
    
    def post_process(self, state: AgentState) -> AgentState:
        """Post-processing hook"""
        self.logger.info(f"Completed {self.name} processing")
        return state
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute agent with pre and post processing"""
        try:
            state = self.pre_process(state)
            state = await self.process(state)
            state = self.post_process(state)
            return state
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {str(e)}")
            state["errors"].append(f"{self.name}: {str(e)}")
            raise AgentException(f"Agent {self.name} failed: {str(e)}")
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "executions": self._execution_count,
            "description": self.description
        }