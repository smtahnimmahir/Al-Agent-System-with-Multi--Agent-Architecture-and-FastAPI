from langgraph.graph import StateGraph, START, END
from app.models.state import AgentState
from app.agents.orchestrator import OrchestratorAgent
from app.agents.data_processor import DataProcessorAgent
from app.agents.decision_maker import DecisionMakerAgent
from app.agents.communicator import CommunicatorAgent
from app.models.schemas import TaskType
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    """Builds and manages the agent execution graph"""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.data_processor = DataProcessorAgent()
        self.decision_maker = DecisionMakerAgent()
        self.communicator = CommunicatorAgent()
    
    def build(self) -> StateGraph:
        """Build the agent graph with dynamic routing"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("orchestrator", self.orchestrator.execute)
        graph.add_node("data_processor", self.data_processor.execute)
        graph.add_node("decision_maker", self.decision_maker.execute)
        graph.add_node("communicator", self.communicator.execute)
        
        # Add edges
        graph.add_edge(START, "orchestrator")
        
        # Conditional routing from orchestrator
        graph.add_conditional_edges(
            "orchestrator",
            self._route_from_orchestrator,
            {
                "data_processor": "data_processor",
                "decision_maker": "decision_maker",
                "communicator": "communicator"
            }
        )
        
        # Conditional routing from data processor
        graph.add_conditional_edges(
            "data_processor",
            self._route_from_data_processor,
            {
                "decision_maker": "decision_maker",
                "communicator": "communicator"
            }
        )
        
        # Decision maker always goes to communicator
        graph.add_edge("decision_maker", "communicator")
        
        # Communicator goes to END
        graph.add_edge("communicator", END)
        
        return graph.compile()
    
    def _route_from_orchestrator(self, state: AgentState) -> str:
        """Determine routing from orchestrator"""
        routing = state.get("metadata", {}).get("routing_decision", {})
        primary_path = routing.get("primary_path", [])
        
        if primary_path:
            # Return the first agent in the path
            next_agent = primary_path[0]
            logger.info(f"Routing from orchestrator to {next_agent}")
            return next_agent
        
        # Default to data processor
        return "data_processor"
    
    def _route_from_data_processor(self, state: AgentState) -> str:
        """Determine routing from data processor"""
        task_type = state.get("task_type", TaskType.GENERAL)
        
        if task_type == TaskType.DECISION_MAKING or "decision" in state["query"].lower():
            logger.info("Routing from data processor to decision maker")
            return "decision_maker"
        
        logger.info("Routing from data processor to communicator")
        return "communicator"

def create_agent_graph():
    """Factory function to create agent graph"""
    builder = GraphBuilder()
    return builder.build()