from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.models.state import AgentState
from app.services.llm_service import get_llm_service
from app.models.schemas import TaskType

class OrchestratorAgent(BaseAgent):
    """Main orchestrator agent that routes queries to appropriate agents"""
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            description="Routes and coordinates tasks between specialized agents"
        )
        self.llm = get_llm_service()
        self.routing_rules = {
            "keywords": {
                "analyze": TaskType.DATA_PROCESSING,
                "decide": TaskType.DECISION_MAKING,
                "calculate": TaskType.DATA_PROCESSING,
                "choose": TaskType.DECISION_MAKING,
                "communicate": TaskType.COMMUNICATION,
                "explain": TaskType.COMMUNICATION,
                "process": TaskType.DATA_PROCESSING
            }
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """Analyze query and determine routing"""
        query = state["query"]
        
        # Determine task type if not specified
        if state["task_type"] == TaskType.GENERAL:
            task_type = await self._determine_task_type(query)
            state["task_type"] = task_type.value
        
        # Determine agent routing path
        routing_path = await self._determine_routing(query, state["task_type"])
        state["metadata"]["routing_decision"] = routing_path
        state["metadata"]["routing_reasoning"] = await self._explain_routing(routing_path, query)
        
        return state
    
    async def _determine_task_type(self, query: str) -> TaskType:
        """Determine the primary task type from the query"""
        # First try keyword matching
        query_lower = query.lower()
        for keyword, task_type in self.routing_rules["keywords"].items():
            if keyword in query_lower:
                return task_type
        
        # Use LLM for complex classification
        prompt = f"""
        Classify this query into one of these task types:
        1. data_processing - For data analysis, calculations, extraction
        2. decision_making - For choices, recommendations, evaluations
        3. communication - For explanations, summaries, presentations
        
        Query: {query}
        
        Respond with only the task type name.
        """
        
        response = await self.llm.ainvoke(prompt)
        task_type_str = response.content.strip().lower()
        
        try:
            return TaskType(task_type_str)
        except ValueError:
            return TaskType.DATA_PROCESSING  # Default
    
    async def _determine_routing(self, query: str, task_type: str) -> Dict[str, Any]:
        """Determine the routing path for agents"""
        routing = {
            "primary_path": [],
            "conditional_paths": {},
            "parallel_processing": False
        }
        
        # Define standard routing patterns
        if task_type == TaskType.DATA_PROCESSING:
            routing["primary_path"] = ["data_processor", "communicator"]
        elif task_type == TaskType.DECISION_MAKING:
            routing["primary_path"] = ["data_processor", "decision_maker", "communicator"]
        elif task_type == TaskType.COMMUNICATION:
            routing["primary_path"] = ["communicator"]
        else:
            # Complex query might need all agents
            routing["primary_path"] = ["data_processor", "decision_maker", "communicator"]
        
        # Check if parallel processing would be beneficial
        if self._needs_parallel_processing(query):
            routing["parallel_processing"] = True
            routing["parallel_agents"] = ["data_processor", "web_searcher"]
        
        return routing
    
    async def _explain_routing(self, routing: Dict[str, Any], query: str) -> str:
        """Generate explanation for routing decision"""
        prompt = f"""
        Explain why this routing path was chosen:
        Query: {query}
        Routing: {routing['primary_path']}
        
        Be concise but clear about the reasoning.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def _needs_parallel_processing(self, query: str) -> bool:
        """Determine if query would benefit from parallel processing"""
        # Simple heuristic - queries with multiple questions or complex requirements
        indicators = ["and", "also", "additionally", "multiple", "various"]
        return any(indicator in query.lower() for indicator in indicators)