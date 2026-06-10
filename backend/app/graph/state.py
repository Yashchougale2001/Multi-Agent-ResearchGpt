# State definitions
from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph.message import add_messages
import operator

class ResearchState(TypedDict):
    """State object for the research workflow"""
    
    # Input
    query: str
    session_id: str
    
    # Planner outputs
    subtasks: Annotated[List[Dict], operator.add]
    planning_thoughts: str
    
    # Research outputs
    research_results: Annotated[List[Dict], operator.add]
    research_metadata: Dict
    
    # Retriever outputs
    retrieved_docs: Annotated[List[Dict], operator.add]
    retrieval_scores: List[float]
    
    # Summarizer outputs
    final_report: str
    summary_metadata: Dict
    
    # Control flow
    current_step: str
    iteration_count: int
    max_iterations: int
    
    # Error handling
    errors: Annotated[List[str], operator.add]
    status: str  # "planning", "researching", "retrieving", "summarizing", "completed", "failed"
    
    # Messages for tracking
    messages: Annotated[List[Dict], add_messages]


class SubTask(TypedDict):
    """Individual subtask structure"""
    id: str
    description: str
    type: str  # "web_search", "api_call", "document_query"
    priority: int
    status: str  # "pending", "in_progress", "completed", "failed"
    result: Optional[Dict]


class ResearchResult(TypedDict):
    """Research result structure"""
    subtask_id: str
    source: str
    content: str
    url: Optional[str]
    timestamp: str
    relevance_score: float


class RetrievedDocument(TypedDict):
    """Retrieved document structure"""
    doc_id: str
    content: str
    metadata: Dict
    similarity_score: float
    source: str