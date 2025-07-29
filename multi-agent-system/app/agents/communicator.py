from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.state import AgentState
from app.services.llm_service import get_llm_service
from app.core.exceptions import CommunicationException

class CommunicatorAgent(BaseAgent):
    """Agent responsible for formatting and communicating results"""
    
    def __init__(self):
        super().__init__(
            name="Communicator",
            description="Formats and presents information in clear, actionable ways"
        )
        self.llm = get_llm_service()
        self.output_formats = ["summary", "detailed", "technical", "executive"]
    
    async def process(self, state: AgentState) -> AgentState:
        """Format and prepare the final communication"""
        try:
            # Determine appropriate communication style
            style = await self._determine_communication_style(state)
            
            # Prepare the message based on all collected information
            message = await self._prepare_message(state, style)
            
            # Add visualizations or formatting if needed
            formatted_output = await self._format_output(message, state)
            
            # Generate actionable insights
            insights = await self._generate_insights(state)
            
            state["final_output"] = formatted_output
            state["metadata"]["communication_style"] = style
            state["metadata"]["insights"] = insights
            state["confidence_scores"]["communication"] = 0.9
            
            return state
            
        except Exception as e:
            raise CommunicationException(f"Communication formatting failed: {str(e)}")
    
    async def _determine_communication_style(self, state: AgentState) -> str:
        """Determine the appropriate communication style"""
        query = state["query"]
        task_type = state["task_type"]
        
        prompt = f"""
        Determine the best communication style for this response:
        Query: {query}
        Task Type: {task_type}
        
        Choose from: technical, executive, casual, detailed
        Consider the audience and purpose.
        
        Respond with just the style name.
        """
        
        response = await self.llm.ainvoke(prompt)
        style = response.content.strip().lower()
        
        return style if style in ["technical", "executive", "casual", "detailed"] else "detailed"
    
    async def _prepare_message(self, state: AgentState, style: str) -> str:
        """Prepare the main message content"""
        processed_data = state.get("processed_data", {})
        decisions = state.get("decisions", [])
        final_decision = state.get("metadata", {}).get("final_decision", {})
        
        prompt = f"""
        Create a {style} response for this query:
        Original Query: {state['query']}
        
        Key Data Points: {processed_data}
        Decision Made: {final_decision.get('selected_option', {}).get('description', 'No decision made')}
        Reasoning: {final_decision.get('reasoning', 'No reasoning provided')}
        
        Structure the response to be clear, actionable, and appropriate for the {style} style.
        Include:
        1. Direct answer to the query
        2. Supporting information
        3. Key recommendations
        4. Next steps if applicable
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _format_output(self, message: str, state: AgentState) -> str:
        """Format the output with appropriate structure"""
        # Add metadata and structure
        output_parts = []
        
        # Header
        output_parts.append(f"## Response to: {state['query']}\n")
        
        # Confidence indicator
        overall_confidence = self._calculate_overall_confidence(state)
        confidence_emoji = "🟢" if overall_confidence > 0.8 else "🟡" if overall_confidence > 0.6 else "🔴"
        output_parts.append(f"**Confidence Level**: {confidence_emoji} {overall_confidence:.0%}\n")
        
        # Main content
        output_parts.append("### Answer")
        output_parts.append(message)
        
        # Add data summary if available
        if state.get("processed_data"):
            output_parts.append("\n### Key Data Points")
            data_summary = self._summarize_data(state["processed_data"])
            output_parts.append(data_summary)
        
        # Add decision summary if available
        if state.get("metadata", {}).get("final_decision"):
            output_parts.append("\n### Decision Summary")
            decision = state["metadata"]["final_decision"]
            output_parts.append(f"- **Selected Option**: {decision.get('selected_option', {}).get('description', 'N/A')}")
            output_parts.append(f"- **Confidence**: {decision.get('confidence', 0):.0%}")
        
        # Add agent path
        output_parts.append(f"\n### Processing Path")
        output_parts.append(f"Agents involved: {' → '.join(state['agent_path'])}")
        
        return "\n".join(output_parts)
    
    async def _generate_insights(self, state: AgentState) -> List[str]:
        """Generate actionable insights from the processing"""
        insights_prompt = f"""
        Based on this processing, generate 3-5 actionable insights:
        Query: {state['query']}
        Data: {state.get('processed_data', {})}
        Decision: {state.get('metadata', {}).get('final_decision', {})}
        
        Make insights specific, actionable, and valuable.
        """
        
        response = await self.llm.ainvoke(insights_prompt)
        
        # Parse insights from response
        insights = []
        for line in response.content.split('\n'):
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                insights.append(line.strip().lstrip('-•').strip())
        
        return insights[:5]  # Limit to 5 insights
    
    def _calculate_overall_confidence(self, state: AgentState) -> float:
        """Calculate overall confidence score"""
        scores = state.get("confidence_scores", {})
        if not scores:
            return 0.5
        
        # Weighted average of all confidence scores
        weights = {
            "data_processing": 0.3,
            "decision_making": 0.4,
            "communication": 0.3
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for key, weight in weights.items():
            if key in scores:
                weighted_sum += scores[key] * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """Summarize processed data for output"""
        summary_parts = []
        
        if "entities" in data and data["entities"]:
            summary_parts.append(f"- **Entities Found**: {', '.join(data['entities'][:5])}")
        
        if "data_points" in data and data["data_points"]:
            for key, values in data["data_points"].items():
                if values:
                    summary_parts.append(f"- **{key.title()}**: {', '.join(str(v) for v in values[:3])}")
        
        if "numerical_analysis" in data:
            summary_parts.append(f"- **Numerical Analysis**: Available")
        
        if "text_analysis" in data:
            summary_parts.append(f"- **Text Analysis**: Completed")
        
        return "\n".join(summary_parts) if summary_parts else "No specific data points extracted"