# Summarizer Agent
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from app.agents.base import BaseAgent
from datetime import datetime


class SummarizerAgent(BaseAgent):
    """Agent responsible for generating comprehensive research reports"""
    
    def __init__(self):
        super().__init__("Summarizer", temperature=0.4)
        
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert research analyst and report writer. Create comprehensive, well-structured research reports.

Your report should include:
1. **Executive Summary** - Key findings in 2-3 sentences
2. **Detailed Analysis** - Organized breakdown of findings
3. **Key Insights** - Bullet points of important discoveries
4. **Sources & Evidence** - Referenced information sources
5. **Conclusion** - Synthesized takeaways

Guidelines:
- Use clear, professional language
- Cite sources when making claims
- Organize information logically
- Highlight contradictions or gaps in research
- Be objective and balanced

Format using Markdown for readability."""),
            ("user", """Original Query: {query}

Research Subtasks Completed:
{subtasks}

Research Results:
{research_results}

Retrieved Documents:
{retrieved_docs}

Create a comprehensive research report:""")
        ])
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final research report"""
        self.log_execution("Generating final report")
        
        try:
            # Prepare data for summarization
            query = state["query"]
            subtasks = state.get("subtasks", [])
            research_results = state.get("research_results", [])
            retrieved_docs = state.get("retrieved_docs", [])
            
            # Format subtasks
            subtasks_text = self._format_subtasks(subtasks)
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            # Format retrieved documents
            docs_text = self._format_documents(retrieved_docs)
            
            # Generate report
            response = self.llm.invoke(
                self.summary_prompt.format_messages(
                    query=query,
                    subtasks=subtasks_text,
                    research_results=research_text,
                    retrieved_docs=docs_text
                )
            )
            
            final_report = response.content
            
            # Add metadata
            metadata = self._create_metadata(
                query, subtasks, research_results, retrieved_docs
            )
            
            self.log_execution("Report generation complete")
            
            return {
                "final_report": final_report,
                "summary_metadata": metadata,
                "current_step": "completed",
                "status": "completed",
                "messages": [self.create_message("assistant", "Research report completed successfully")]
            }
            
        except Exception as e:
            self.log_execution(f"Summarization failed: {str(e)}", "error")
            return {
                "errors": [f"Summarization error: {str(e)}"],
                "status": "failed"
            }
    
    def _format_subtasks(self, subtasks: List[Dict]) -> str:
        """Format subtasks for prompt"""
        formatted = []
        for idx, task in enumerate(subtasks, 1):
            formatted.append(
                f"{idx}. [{task['type']}] {task['description']} "
                f"(Priority: {task['priority']}, Status: {task['status']})"
            )
        return "\n".join(formatted) if formatted else "No subtasks completed"
    
    def _format_research_results(self, results: List[Dict]) -> str:
        """Format research results for prompt"""
        if not results:
            return "No research results available"
        
        formatted = []
        for idx, result in enumerate(results[:10], 1):  # Limit to top 10
            formatted.append(
                f"\n--- Result {idx} ---\n"
                f"Source: {result['source']}\n"
                f"Relevance: {result.get('relevance_score', 'N/A')}\n"
                f"Content:\n{result['content'][:500]}...\n"
            )
        return "\n".join(formatted)
    
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format retrieved documents for prompt"""
        if not documents:
            return "No documents retrieved"
        
        formatted = []
        for idx, doc in enumerate(documents[:5], 1):  # Top 5 documents
            formatted.append(
                f"\n--- Document {idx} ---\n"
                f"Similarity Score: {doc['similarity_score']:.2f}\n"
                f"Source: {doc['source']}\n"
                f"Content:\n{doc['content'][:500]}...\n"
            )
        return "\n".join(formatted)
    
    def _create_metadata(
        self, 
        query: str, 
        subtasks: List[Dict],
        research_results: List[Dict],
        retrieved_docs: List[Dict]
    ) -> Dict:
        """Create summary metadata"""
        return {
            "query": query,
            "total_subtasks": len(subtasks),
            "completed_subtasks": len([t for t in subtasks if t["status"] == "completed"]),
            "total_research_results": len(research_results),
            "total_documents_retrieved": len(retrieved_docs),
            "avg_document_relevance": sum(d["similarity_score"] for d in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0,
            "timestamp": datetime.now().isoformat(),
            "sources": list(set(r["source"] for r in research_results))
        }