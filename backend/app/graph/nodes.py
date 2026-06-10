# Graph nodes
from typing import Dict, Any, Callable
from app.graph.state import ResearchState
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearchAgent
from app.agents.retriever import RetrieverAgent
from app.agents.summarizer import SummarizerAgent
import logging

logger = logging.getLogger(__name__)


class GraphNodes:
    """
    Node definitions for the LangGraph workflow.
    Each node represents a step in the research pipeline.
    """
    
    def __init__(self):
        """Initialize all agents"""
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.retriever = RetrieverAgent()
        self.summarizer = SummarizerAgent()
        
        logger.info("Graph nodes initialized")
    
    def planner_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Planner node: Decompose query into actionable subtasks
        
        Input state: query, session_id
        Output: subtasks, planning_thoughts, status update
        """
        logger.info(f"Executing Planner Node for session: {state.get('session_id')}")
        
        try:
            # Execute planner agent
            result = self.planner.execute(state)
            
            # Add execution metadata
            result["messages"] = result.get("messages", []) + [{
                "role": "system",
                "content": f"Planner created {len(result.get('subtasks', []))} subtasks",
                "agent": "Planner"
            }]
            
            return result
            
        except Exception as e:
            logger.error(f"Planner node failed: {str(e)}")
            return {
                "status": "failed",
                "errors": [f"Planner error: {str(e)}"],
                "messages": [{
                    "role": "system",
                    "content": f"Planner failed: {str(e)}",
                    "agent": "Planner"
                }]
            }
    
    def researcher_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Researcher node: Gather information for each subtask
        
        Input state: subtasks
        Output: research_results, research_metadata, status update
        """
        logger.info(f"Executing Researcher Node for session: {state.get('session_id')}")
        
        try:
            # Execute researcher agent
            result = self.researcher.execute(state)
            
            # Add execution metadata
            result["messages"] = result.get("messages", []) + [{
                "role": "system",
                "content": f"Researcher gathered {len(result.get('research_results', []))} results",
                "agent": "Researcher"
            }]
            
            return result
            
        except Exception as e:
            logger.error(f"Researcher node failed: {str(e)}")
            return {
                "status": "failed",
                "errors": [f"Researcher error: {str(e)}"],
                "messages": [{
                    "role": "system",
                    "content": f"Researcher failed: {str(e)}",
                    "agent": "Researcher"
                }]
            }
    
    def retriever_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Retriever node: Query ChromaDB for relevant documents using RAG
        
        Input state: query, research_results
        Output: retrieved_docs, retrieval_scores, status update
        """
        logger.info(f"Executing Retriever Node for session: {state.get('session_id')}")
        
        try:
            # Execute retriever agent
            result = self.retriever.execute(state)
            
            # Add execution metadata
            result["messages"] = result.get("messages", []) + [{
                "role": "system",
                "content": f"Retriever found {len(result.get('retrieved_docs', []))} relevant documents",
                "agent": "Retriever"
            }]
            
            return result
            
        except Exception as e:
            logger.error(f"Retriever node failed: {str(e)}")
            return {
                "status": "failed",
                "errors": [f"Retriever error: {str(e)}"],
                "messages": [{
                    "role": "system",
                    "content": f"Retriever failed: {str(e)}",
                    "agent": "Retriever"
                }]
            }
    
    def summarizer_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Summarizer node: Generate comprehensive final report
        
        Input state: query, subtasks, research_results, retrieved_docs
        Output: final_report, summary_metadata, status update
        """
        logger.info(f"Executing Summarizer Node for session: {state.get('session_id')}")
        
        try:
            # Execute summarizer agent
            result = self.summarizer.execute(state)
            
            # Add execution metadata
            result["messages"] = result.get("messages", []) + [{
                "role": "system",
                "content": "Summarizer completed final report generation",
                "agent": "Summarizer"
            }]
            
            return result
            
        except Exception as e:
            logger.error(f"Summarizer node failed: {str(e)}")
            return {
                "status": "failed",
                "errors": [f"Summarizer error: {str(e)}"],
                "messages": [{
                    "role": "system",
                    "content": f"Summarizer failed: {str(e)}",
                    "agent": "Summarizer"
                }]
            }
    
    def error_handler_node(self, state: ResearchState) -> Dict[str, Any]:
        """
        Error handler node: Handle workflow errors gracefully
        
        Input state: errors
        Output: error summary, recovery suggestions
        """
        logger.error(f"Error handler node activated for session: {state.get('session_id')}")
        
        errors = state.get("errors", [])
        
        return {
            "status": "failed",
            "final_report": f"# Research Failed\n\nThe research process encountered errors:\n\n" + 
                          "\n".join([f"- {error}" for error in errors]),
            "summary_metadata": {
                "status": "failed",
                "errors": errors,
                "partial_results": len(state.get("research_results", []))
            },
            "messages": [{
                "role": "system",
                "content": f"Workflow failed with {len(errors)} errors",
                "agent": "ErrorHandler"
            }]
        }
    
    def conditional_edge_router(self, state: ResearchState) -> str:
        """
        Conditional routing logic for the graph
        
        Determines the next node based on current state
        """
        current_step = state.get("current_step", "")
        status = state.get("status", "")
        
        # Check for errors
        if status == "failed" or state.get("errors"):
            return "error_handler"
        
        # Route based on current step
        if current_step == "planning_complete":
            return "researcher"
        elif current_step == "research_complete":
            return "retriever"
        elif current_step == "retrieval_complete":
            return "summarizer"
        elif current_step == "completed":
            return "end"
        else:
            return "planner"
    
    def should_continue(self, state: ResearchState) -> bool:
        """
        Determine if workflow should continue or terminate
        
        Returns True if workflow should continue, False to end
        """
        status = state.get("status", "")
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 10)
        
        # End if completed or failed
        if status in ["completed", "failed"]:
            return False
        
        # End if max iterations reached
        if iteration_count >= max_iterations:
            logger.warning(f"Max iterations ({max_iterations}) reached")
            return False
        
        return True


# Create singleton instance
graph_nodes = GraphNodes()


# Helper functions for node creation

def create_planner_node() -> Callable:
    """Create planner node function"""
    return graph_nodes.planner_node


def create_researcher_node() -> Callable:
    """Create researcher node function"""
    return graph_nodes.researcher_node


def create_retriever_node() -> Callable:
    """Create retriever node function"""
    return graph_nodes.retriever_node


def create_summarizer_node() -> Callable:
    """Create summarizer node function"""
    return graph_nodes.summarizer_node


def create_error_handler_node() -> Callable:
    """Create error handler node function"""
    return graph_nodes.error_handler_node