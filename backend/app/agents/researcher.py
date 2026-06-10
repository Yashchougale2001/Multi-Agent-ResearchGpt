# Research Agent
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from app.agents.base import BaseAgent
from app.graph.state import ResearchResult
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio


class ResearchAgent(BaseAgent):
    """Agent responsible for gathering information from various sources"""
    
    def __init__(self):
        super().__init__("Researcher", temperature=0.5)
        
        self.search_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research assistant. Given search results, extract and synthesize the most relevant information.

Focus on:
- Factual accuracy
- Recency of information
- Credibility of sources
- Relevance to the research question

Provide a concise summary with key findings."""),
            ("user", "Subtask: {subtask}\n\nSearch Results:\n{results}\n\nSummarize key findings:")
        ])
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research for all pending subtasks"""
        self.log_execution("Starting research phase")
        
        subtasks = state.get("subtasks", [])
        research_results = []
        
        try:
            for subtask in subtasks:
                if subtask["status"] == "pending":
                    self.log_execution(f"Researching: {subtask['description']}")
                    
                    # Perform search based on task type
                    if subtask["type"] == "web_search":
                        results = self._web_search(subtask)
                    elif subtask["type"] == "document_query":
                        results = self._document_query(subtask)
                    else:
                        results = self._generic_research(subtask)
                    
                    research_results.extend(results)
                    subtask["status"] = "completed"
            
            self.log_execution(f"Research complete: {len(research_results)} results")
            
            return {
                "research_results": research_results,
                "research_metadata": {
                    "total_results": len(research_results),
                    "timestamp": datetime.now().isoformat()
                },
                "current_step": "research_complete",
                "status": "retrieving",
                "messages": [self.create_message("assistant", f"Gathered {len(research_results)} research results")]
            }
            
        except Exception as e:
            self.log_execution(f"Research failed: {str(e)}", "error")
            return {
                "errors": [f"Research error: {str(e)}"],
                "status": "failed"
            }
    
    def _web_search(self, subtask: Dict) -> List[Dict]:
        """Perform web search (simulated - replace with actual search API)"""
        # In production, integrate with Google Search API, Bing API, or SerpAPI
        results = []
        
        # Simulated search results
        search_queries = subtask.get("search_queries", [subtask["description"]])
        
        for query in search_queries[:3]:  # Limit queries
            result = {
                "subtask_id": subtask["id"],
                "source": "web_search",
                "content": f"Research findings for: {query}\n\n[In production, this would contain actual web search results]",
                "url": f"https://example.com/search?q={query}",
                "timestamp": datetime.now().isoformat(),
                "relevance_score": 0.85,
                "query": query
            }
            results.append(result)
        
        return results
    
    def _document_query(self, subtask: Dict) -> List[Dict]:
        """Query internal documents (handled by Retriever Agent later)"""
        return [{
            "subtask_id": subtask["id"],
            "source": "document_query",
            "content": f"Document query prepared for: {subtask['description']}",
            "timestamp": datetime.now().isoformat(),
            "relevance_score": 0.9
        }]
    
    def _generic_research(self, subtask: Dict) -> List[Dict]:
        """Generic research using LLM"""
        try:
            response = self.llm.invoke(
                f"Research task: {subtask['description']}\n\nProvide detailed information:"
            )
            
            return [{
                "subtask_id": subtask["id"],
                "source": "llm_research",
                "content": response.content,
                "timestamp": datetime.now().isoformat(),
                "relevance_score": 0.75
            }]
        except Exception as e:
            self.log_execution(f"Generic research failed: {str(e)}", "error")
            return []