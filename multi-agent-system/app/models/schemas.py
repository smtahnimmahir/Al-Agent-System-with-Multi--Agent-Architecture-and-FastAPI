from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class TaskType(str, Enum):
    """Enumeration of available task types"""
    DATA_PROCESSING = "data_processing"
    DECISION_MAKING = "decision_making"
    COMMUNICATION = "communication"
    GENERAL = "general"

class AgentRequest(BaseModel):
    """Request model for agent operations"""
    query: str = Field(..., min_length=1, description="User query or task description")
    task_type: Optional[TaskType] = Field(default=TaskType.GENERAL, description="Specific task type")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Request metadata")
    
    @validator('query')
    def validate_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v

class AgentResponse(BaseModel):
    """Response model for agent operations"""
    result: str = Field(..., description="Agent processing result")
    task_type: TaskType = Field(..., description="Task type that was processed")
    agent_path: List[str] = Field(..., description="Agents involved in processing")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in result")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")