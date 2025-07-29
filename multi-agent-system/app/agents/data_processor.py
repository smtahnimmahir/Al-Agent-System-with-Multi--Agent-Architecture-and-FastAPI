import json
import re
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.models.state import AgentState
from app.services.llm_service import get_llm_service
from app.core.exceptions import DataProcessingException

class DataProcessorAgent(BaseAgent):
    """Agent responsible for data processing and transformation"""
    
    def __init__(self):
        super().__init__(
            name="DataProcessor",
            description="Processes and transforms data, extracts insights, and prepares information"
        )
        self.llm = get_llm_service()
    
    async def process(self, state: AgentState) -> AgentState:
        """Process data and extract structured information"""
        try:
            query = state["query"]
            
            # Analyze the query type and extract data requirements
            analysis_prompt = f"""
            Analyze this query and extract key data points and requirements:
            Query: {query}
            
            Provide a structured analysis including:
            1. Data types needed
            2. Key entities mentioned
            3. Required transformations
            4. Output format requirements
            
            Respond in JSON format.
            """
            
            response = await self.llm.ainvoke(analysis_prompt)
            
            try:
                analysis = json.loads(response.content)
            except:
                # Fallback to text processing
                analysis = self._extract_data_from_text(response.content)
            
            # Process based on data type
            processed_data = {
                "raw_query": query,
                "analysis": analysis,
                "entities": self._extract_entities(query),
                "data_points": self._extract_data_points(query),
                "structured_output": None
            }
            
            # If numerical data, process calculations
            if self._contains_numerical_data(query):
                processed_data["numerical_analysis"] = await self._process_numerical_data(query)
            
            # If text data, process and structure
            if self._contains_text_data(query):
                processed_data["text_analysis"] = await self._process_text_data(query)
            
            state["processed_data"] = processed_data
            state["confidence_scores"]["data_processing"] = 0.85
            
            return state
            
        except Exception as e:
            raise DataProcessingException(f"Data processing failed: {str(e)}")
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        # Simple entity extraction (can be enhanced with NLP libraries)
        entities = []
        # Extract capitalized words (simple approach)
        entities.extend(re.findall(r'\b[A-Z][a-z]+\b', text))
        return list(set(entities))
    
    def _extract_data_points(self, text: str) -> Dict[str, Any]:
        """Extract specific data points from text"""
        data_points = {}
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        if numbers:
            data_points["numbers"] = numbers
        
        # Extract dates (simple pattern)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        if dates:
            data_points["dates"] = dates
        
        # Extract emails
        emails = re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
        if emails:
            data_points["emails"] = emails
        
        return data_points
    
    def _contains_numerical_data(self, text: str) -> bool:
        """Check if text contains numerical data"""
        return bool(re.search(r'\d+', text))
    
    def _contains_text_data(self, text: str) -> bool:
        """Check if text contains substantial text data"""
        return len(text.split()) > 5
    
    async def _process_numerical_data(self, text: str) -> Dict[str, Any]:
        """Process numerical data in the text"""
        prompt = f"""
        Extract and analyze all numerical data from this text:
        {text}
        
        Provide:
        1. All numbers found
        2. Their context
        3. Any calculations needed
        4. Statistical summary if applicable
        """
        
        response = await self.llm.ainvoke(prompt)
        return {"analysis": response.content}
    
    async def _process_text_data(self, text: str) -> Dict[str, Any]:
        """Process and structure text data"""
        prompt = f"""
        Analyze and structure this text data:
        {text}
        
        Provide:
        1. Main topics
        2. Key points
        3. Sentiment if applicable
        4. Summary
        """
        
        response = await self.llm.ainvoke(prompt)
        return {"analysis": response.content}
    
    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback method to extract data from unstructured text"""
        return {
            "raw_analysis": text,
            "extraction_method": "fallback"
        }