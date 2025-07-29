from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import AgentRequest, AgentResponse, ErrorResponse
from app.services.graph_builder import create_agent_graph
from app.models.state import AgentState
from app.core.logging import setup_logging
import time
from typing import Dict, Any

logger = setup_logging()
router = APIRouter(prefix="/api/v1", tags=["agents"])

# Create agent graph on startup
agent_graph = create_agent_graph()

@router.post(
    "/process",
    response_model=AgentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def process_query(request: AgentRequest) -> AgentResponse:
    """
    Process a query through the multi-agent system
    
    The system will automatically route the query through appropriate agents
    based on the task type and content.
    """
    start_time = time.time()
    
    try:
        # Initialize state
        state: AgentState = {
            "messages": [request.query],
            "query": request.query,
            "task_type": request.task_type.value,
            "processed_data": None,
            "decisions": None,
            "final_output": None,
            "agent_path": [],
            "confidence_scores": {},
            "errors": [],
            "metadata": request.metadata or {}
        }
        
        # Add context to state if provided
        if request.context:
            state["metadata"]["context"] = request.context
        
        logger.info(f"Processing query: {request.query[:50]}...")
        
        # Execute agent graph
        result = await agent_graph.ainvoke(state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract confidence score
        overall_confidence = sum(result["confidence_scores"].values()) / len(result["confidence_scores"]) if result["confidence_scores"] else 0.5
        
        return AgentResponse(
            result=result["final_output"] or "No output generated",
            task_type=result["task_type"],
            agent_path=result["agent_path"],
            confidence_score=overall_confidence,
            processing_time=processing_time,
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "multi-agent-system"}

@router.get("/agents")
async def list_agents() -> Dict[str, Any]:
    """List all available agents and their capabilities"""
    from app.agents import orchestrator, data_processor, decision_maker, communicator
    
    agents_info = {
        "orchestrator": {
            "name": "Orchestrator",
            "description": "Routes and coordinates tasks between specialized agents",
            "capabilities": ["task routing", "agent coordination", "query analysis"]
        },
        "data_processor": {
            "name": "Data Processor",
            "description": "Processes and transforms data, extracts insights",
            "capabilities": ["data extraction", "transformation", "analysis", "entity recognition"]
        },
        "decision_maker": {
            "name": "Decision Maker",
            "description": "Makes informed decisions based on data and context",
            "capabilities": ["option generation", "evaluation", "recommendation", "validation"]
        },
        "communicator": {
            "name": "Communicator",
            "description": "Formats and presents information clearly",
            "capabilities": ["formatting", "summarization", "insight generation", "style adaptation"]
        }
    }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info),
        "task_types": ["data_processing", "decision_making", "communication", "general"]
    }