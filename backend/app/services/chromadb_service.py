import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from app.config import settings
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB vector store with local embeddings"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Use custom embedding function with sentence-transformers
        class LocalEmbeddingFunction:
            def __call__(self, input: List[str]) -> List[List[float]]:
                return llm_service.generate_embeddings(input)
        
        self.embedding_function = LocalEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized with local embeddings: {settings.CHROMA_COLLECTION_NAME}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]) -> bool:
        """Add documents to the collection"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            return False
    
    def query(self, query_text: str, n_results: int = 5, where: Optional[Dict] = None) -> Dict:
        """Query the collection"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            logger.info(f"Query returned {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "embedding_model": settings.EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"total_documents": 0, "error": str(e)}
    
    def delete_collection(self):
        """Delete the collection"""
        try:
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            logger.info(f"Deleted collection: {settings.CHROMA_COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")


# Singleton instance
chroma_service = ChromaDBService()