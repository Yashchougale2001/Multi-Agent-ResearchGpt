from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents using Groq"""
    
    def __init__(self, name: str, temperature: float = 0.7):
        self.name = name
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=settings.MAX_TOKENS
        )
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def log_execution(self, message: str, level: str = "info"):
        """Log agent execution"""
        log_method = getattr(self.logger, level)
        log_method(f"[{self.name}] {message}")
    
    def create_message(self, role: str, content: str) -> Dict:
        """Create a message for state tracking"""
        return {
            "role": role,
            "content": content,
            "agent": self.name
        }