# LangGraph workflow
from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearchAgent
from app.agents.retriever import RetrieverAgent
from app.agents.summarizer import SummarizerAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """LangGraph workflow orchestrating all agents"""
    
    def __init__(self):
        # Initialize agents
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.retriever = RetrieverAgent()
        self.summarizer = SummarizerAgent()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        
        # Create graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("retriever", self._retriever_node)
        workflow.add_node("summarizer", self._summarizer_node)
        
        # Add edges
        workflow.set_entry_point("planner")
        
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "retriever")
        workflow.add_edge("retriever", "summarizer")
        workflow.add_edge("summarizer", END)
        
        # Compile
        return workflow.compile()
    
    def _planner_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute planner agent"""
        logger.info("Executing Planner Node")
        result = self.planner.execute(state)
        return result
    
    def _researcher_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute researcher agent"""
        logger.info("Executing Researcher Node")
        result = self.researcher.execute(state)
        return result
    
    def _retriever_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute retriever agent"""
        logger.info("Executing Retriever Node")
        result = self.retriever.execute(state)
        return result
    
    def _summarizer_node(self, state: ResearchState) -> Dict[str, Any]:
        """Execute summarizer agent"""
        logger.info("Executing Summarizer Node")
        result = self.summarizer.execute(state)
        return result
    
    async def execute(self, query: str, session_id: str) -> Dict[str, Any]:
        """Execute the complete research workflow"""
        logger.info(f"Starting research workflow for session: {session_id}")
        
        # Initialize state
        initial_state: ResearchState = {
            "query": query,
            "session_id": session_id,
            "subtasks": [],
            "planning_thoughts": "",
            "research_results": [],
            "research_metadata": {},
            "retrieved_docs": [],
            "retrieval_scores": [],
            "final_report": "",
            "summary_metadata": {},
            "current_step": "initialized",
            "iteration_count": 0,
            "max_iterations": 10,
            "errors": [],
            "status": "planning",
            "messages": []
        }
        
        # Execute graph
        try:
            final_state = await self.graph.ainvoke(initial_state)
            logger.info(f"Workflow completed for session: {session_id}")
            return final_state
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {
                **initial_state,
                "status": "failed",
                "errors": [str(e)]
            }


# Singleton instance
research_workflow = ResearchWorkflow()