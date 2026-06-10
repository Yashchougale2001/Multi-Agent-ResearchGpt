# Retriever Agent
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from app.agents.base import BaseAgent
from app.services.chromadb_service import chroma_service
from app.config import settings
import uuid


class RetrieverAgent(BaseAgent):
    """Agent responsible for RAG-based document retrieval"""
    
    def __init__(self):
        super().__init__("Retriever", temperature=0.2)
        
        self.rerank_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document relevance expert. Given a query and retrieved documents, assess their relevance.

Rate each document's relevance to the query on a scale of 0-1, where:
- 1.0 = Highly relevant, directly answers the query
- 0.5 = Partially relevant, contains some useful information
- 0.0 = Not relevant

Return ONLY a JSON array of scores: [0.95, 0.72, 0.31, ...]"""),
            ("user", "Query: {query}\n\nDocuments:\n{documents}\n\nRelevance scores:")
        ])
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and rank relevant documents"""
        self.log_execution("Starting document retrieval")
        
        query = state["query"]
        research_results = state.get("research_results", [])
        
        try:
            # First, add research results to ChromaDB for unified retrieval
            if research_results:
                self._index_research_results(research_results)
            
            # Retrieve relevant documents
            retrieved_docs = self._retrieve_documents(query)
            
            # Re-rank documents
            if retrieved_docs:
                reranked_docs = self._rerank_documents(query, retrieved_docs)
            else:
                reranked_docs = []
            
            self.log_execution(f"Retrieved {len(reranked_docs)} relevant documents")
            
            return {
                "retrieved_docs": reranked_docs,
                "retrieval_scores": [doc["similarity_score"] for doc in reranked_docs],
                "current_step": "retrieval_complete",
                "status": "summarizing",
                "messages": [self.create_message("assistant", f"Retrieved {len(reranked_docs)} relevant documents")]
            }
            
        except Exception as e:
            self.log_execution(f"Retrieval failed: {str(e)}", "error")
            return {
                "errors": [f"Retrieval error: {str(e)}"],
                "status": "failed"
            }
    
    def _index_research_results(self, research_results: List[Dict]):
        """Index research results into ChromaDB"""
        documents = []
        metadatas = []
        ids = []
        
        for result in research_results:
            documents.append(result["content"])
            metadatas.append({
                "source": result["source"],
                "timestamp": result["timestamp"],
                "relevance_score": result.get("relevance_score", 0.5),
                "subtask_id": result.get("subtask_id", "unknown")
            })
            ids.append(str(uuid.uuid4()))
        
        if documents:
            chroma_service.add_documents(documents, metadatas, ids)
            self.log_execution(f"Indexed {len(documents)} research results")
    
    def _retrieve_documents(self, query: str) -> List[Dict]:
        """Retrieve documents from ChromaDB"""
        results = chroma_service.query(
            query_text=query,
            n_results=settings.RETRIEVAL_TOP_K
        )
        
        retrieved_docs = []
        
        if results["documents"] and results["documents"][0]:
            for idx, doc in enumerate(results["documents"][0]):
                retrieved_doc = {
                    "doc_id": str(uuid.uuid4()),
                    "content": doc,
                    "metadata": results["metadatas"][0][idx] if results["metadatas"] else {},
                    "similarity_score": 1 - results["distances"][0][idx],  # Convert distance to similarity
                    "source": results["metadatas"][0][idx].get("source", "unknown") if results["metadatas"] else "unknown"
                }
                retrieved_docs.append(retrieved_doc)
        
        return retrieved_docs
    
    def _rerank_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Re-rank documents using LLM"""
        try:
            # Prepare documents for reranking
            doc_texts = "\n\n---\n\n".join([
                f"Document {idx + 1}:\n{doc['content'][:500]}"
                for idx, doc in enumerate(documents)
            ])
            
            # Get relevance scores from LLM
            response = self.llm.invoke(
                self.rerank_prompt.format_messages(
                    query=query,
                    documents=doc_texts
                )
            )
            
            # Parse scores (simplified - in production, use more robust parsing)
            scores = self._parse_scores(response.content, len(documents))
            
            # Update similarity scores
            for idx, doc in enumerate(documents):
                if idx < len(scores):
                    doc["similarity_score"] = scores[idx]
            
            # Sort by score
            documents.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return documents
            
        except Exception as e:
            self.log_execution(f"Reranking failed: {str(e)}, using original scores", "warning")
            return documents
    
    def _parse_scores(self, content: str, expected_count: int) -> List[float]:
        """Parse relevance scores from LLM response"""
        try:
            import json
            # Try to find JSON array
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                scores = json.loads(json_str)
                return scores[:expected_count]
            else:
                return [0.5] * expected_count
        except:
            return [0.5] * expected_count