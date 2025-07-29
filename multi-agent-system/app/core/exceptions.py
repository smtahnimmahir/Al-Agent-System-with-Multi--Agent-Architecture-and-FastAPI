class AgentException(Exception):
    """Base exception for agent-related errors"""
    pass

class DataProcessingException(AgentException):
    """Raised when data processing fails"""
    pass

class DecisionMakingException(AgentException):
    """Raised when decision-making process fails"""
    pass

class CommunicationException(AgentException):
    """Raised when communication between agents fails"""
    pass

class LLMException(AgentException):
    """Raised when LLM operations fail"""
    pass