from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.models.state import AgentState
from app.services.llm_service import get_llm_service
from app.services.tools import web_search, calculate_metrics
from app.core.exceptions import DecisionMakingException

class DecisionMakerAgent(BaseAgent):
    """Agent responsible for making decisions based on processed data"""
    
    def __init__(self):
        super().__init__(
            name="DecisionMaker",
            description="Makes informed decisions based on data and context"
        )
        self.llm = get_llm_service()
        self.decision_criteria = {
            "confidence_threshold": 0.7,
            "min_data_points": 2,
            "require_validation": True
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """Make decisions based on processed data"""
        try:
            processed_data = state.get("processed_data", {})
            query = state["query"]
            
            # Generate decision options
            options = await self._generate_options(query, processed_data)
            
            # Evaluate each option
            evaluated_options = []
            for option in options:
                evaluation = await self._evaluate_option(option, processed_data)
                evaluated_options.append(evaluation)
            
            # Make final decision
            decision = await self._make_decision(evaluated_options, processed_data)
            
            # Validate decision if required
            if self.decision_criteria["require_validation"]:
                decision = await self._validate_decision(decision, state)
            
            state["decisions"] = evaluated_options
            state["metadata"]["final_decision"] = decision
            state["confidence_scores"]["decision_making"] = decision.get("confidence", 0.8)
            
            return state
            
        except Exception as e:
            raise DecisionMakingException(f"Decision making failed: {str(e)}")
    
    async def _generate_options(self, query: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate decision options based on query and data"""
        prompt = f"""
        Based on this query and data, generate 3 possible decision options:
        Query: {query}
        Data Summary: {data.get('analysis', 'No data available')}
        
        For each option provide:
        1. Option description
        2. Pros and cons
        3. Required resources
        4. Expected outcome
        
        Format as a list of options.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Parse options from response
        options = []
        option_texts = response.content.split('\n\n')
        
        for i, option_text in enumerate(option_texts[:3]):
            options.append({
                "id": f"option_{i+1}",
                "description": option_text,
                "raw_text": option_text
            })
        
        return options
    
    async def _evaluate_option(self, option: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single option"""
        prompt = f"""
        Evaluate this decision option:
        Option: {option['description']}
        Context Data: {data}
        
        Provide:
        1. Feasibility score (0-1)
        2. Impact score (0-1)
        3. Risk assessment
        4. Implementation complexity
        5. Overall recommendation
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Extract scores from response
        evaluation = {
            "option_id": option["id"],
            "description": option["description"],
            "evaluation": response.content,
            "scores": self._extract_scores(response.content)
        }
        
        return evaluation
    
    async def _make_decision(self, evaluations: List[Dict[str, Any]], data: Dict[str, Any]) -> Dict[str, Any]:
        """Make final decision based on evaluations"""
        # Calculate weighted scores
        best_option = None
        best_score = 0
        
        for evaluation in evaluations:
            scores = evaluation.get("scores", {})
            weighted_score = (
                scores.get("feasibility", 0) * 0.3 +
                scores.get("impact", 0) * 0.4 +
                (1 - scores.get("risk", 0)) * 0.3
            )
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_option = evaluation
        
        # Get additional context for decision
        if best_score < self.decision_criteria["confidence_threshold"]:
            # Need more information
            additional_info = await self._gather_additional_info(evaluations)
            best_option["additional_context"] = additional_info
        
        decision = {
            "selected_option": best_option,
            "confidence": best_score,
            "reasoning": await self._generate_reasoning(best_option, evaluations),
            "alternatives_considered": len(evaluations)
        }
        
        return decision
    
    async def _validate_decision(self, decision: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Validate the decision with additional checks"""
        # Search for supporting information
        query = f"{state['query']} {decision['selected_option']['description']}"
        search_results = await web_search(query)
        
        validation_prompt = f"""
        Validate this decision with supporting evidence:
        Decision: {decision['selected_option']['description']}
        Evidence: {search_results}
        
        Is this decision well-supported? Provide confidence level and any concerns.
        """
        
        response = await self.llm.ainvoke(validation_prompt)
        decision["validation"] = response.content
        
        return decision
    
    async def _gather_additional_info(self, evaluations: List[Dict[str, Any]]) -> str:
        """Gather additional information when confidence is low"""
        search_query = f"best practices {evaluations[0]['description']}"
        results = await web_search(search_query)
        return results
    
    async def _generate_reasoning(self, selected: Dict[str, Any], all_options: List[Dict[str, Any]]) -> str:
        """Generate reasoning for the decision"""
        prompt = f"""
        Explain why this option was selected:
        Selected: {selected['description']}
        All options considered: {len(all_options)}
        
        Provide clear reasoning focusing on:
        1. Key advantages
        2. How it addresses the original query
        3. Why it's better than alternatives
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def _extract_scores(self, text: str) -> Dict[str, float]:
        """Extract numerical scores from evaluation text"""
        import re
        
        scores = {}
        
        # Try to find scores in format "score: 0.8" or "8/10"
        patterns = {
            "feasibility": r"feasibility.*?(\d*\.?\d+)",
            "impact": r"impact.*?(\d*\.?\d+)",
            "risk": r"risk.*?(\d*\.?\d+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                score = float(match.group(1))
                # Normalize to 0-1 if needed
                if score > 1:
                    score = score / 10
                scores[key] = score
            else:
                scores[key] = 0.5  # Default middle score
        
        return scores