from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated

class AgentState(TypedDict):
    """State management for agent communication"""
    messages: Annotated[List[str], "add_messages"]
    query: str
    task_type: str
    processed_data: Optional[Dict[str, Any]]
    decisions: Optional[List[Dict[str, Any]]]
    final_output: Optional[str]
    agent_path: List[str]
    confidence_scores: Dict[str, float]
    errors: List[str]
    metadata: Dict[str, Any]