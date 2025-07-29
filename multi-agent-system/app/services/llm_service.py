from langchain_groq import ChatGroq
from app.core.config import get_settings
from app.core.exceptions import LLMException
from functools import lru_cache
import asyncio
from typing import Optional, Any

class LLMService:
    """Service for managing LLM interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatGroq(
            model=self.settings.llm_model,
            groq_api_key=self.settings.groq_api_key,
            temperature=self.settings.temperature,
            max_retries=self.settings.max_retries
        )
    
    async def ainvoke(self, prompt: str, **kwargs) -> Any:
        """Async invoke LLM with error handling"""
        try:
            response = await self.llm.ainvoke(prompt, **kwargs)
            return response
        except Exception as e:
            raise LLMException(f"LLM invocation failed: {str(e)}")
    
    def invoke(self, prompt: str, **kwargs) -> Any:
        """Sync invoke LLM with error handling"""
        try:
            response = self.llm.invoke(prompt, **kwargs)
            return response
        except Exception as e:
            raise LLMException(f"LLM invocation failed: {str(e)}")

@lru_cache()
def get_llm_service() -> LLMService:
    """Get cached LLM service instance"""
    return LLMService()