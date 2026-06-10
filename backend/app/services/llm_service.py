from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import asyncio
from functools import lru_cache
import numpy as np

logger = logging.getLogger(__name__)


class LLMService:
    """
    Centralized service for all LLM interactions using Groq API (FREE).
    Uses sentence-transformers for embeddings (local, no API costs).
    """
    
    def __init__(self):
        """Initialize LLM service with Groq and local embeddings"""
        self._chat_model = None
        self._embeddings_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize Groq chat model and local embedding model"""
        try:
            # Groq Chat Model (FREE - Llama 3)
            self._chat_model = ChatGroq(
                model=settings.GROQ_MODEL,
                groq_api_key=settings.GROQ_API_KEY,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                max_retries=3
            )
            
            # Local Sentence Transformer for Embeddings (FREE)
            self._embeddings_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            logger.info(f"LLM service initialized with Groq ({settings.GROQ_MODEL}) and {settings.EMBEDDING_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise
    
    @property
    def chat_model(self) -> ChatGroq:
        """Get Groq chat model instance"""
        if self._chat_model is None:
            self._initialize_models()
        return self._chat_model
    
    @property
    def embeddings_model(self) -> SentenceTransformer:
        """Get local embeddings model instance"""
        if self._embeddings_model is None:
            self._initialize_models()
        return self._embeddings_model
    
    async def generate_response(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from Groq LLM
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            temp = temperature if temperature is not None else settings.TEMPERATURE
            tokens = max_tokens if max_tokens is not None else settings.MAX_TOKENS
            
            model = ChatGroq(
                model=settings.GROQ_MODEL,
                groq_api_key=settings.GROQ_API_KEY,
                temperature=temp,
                max_tokens=tokens
            )
            
            response = await model.ainvoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
            raise
    
    async def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any],
        temperature: float = None
    ) -> str:
        """
        Generate response using a template with Groq
        
        Args:
            template: Prompt template string
            variables: Template variables
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            temp = temperature if temperature is not None else settings.TEMPERATURE
            
            prompt = ChatPromptTemplate.from_template(template)
            
            model = ChatGroq(
                model=settings.GROQ_MODEL,
                groq_api_key=settings.GROQ_API_KEY,
                temperature=temp,
                max_tokens=settings.MAX_TOKENS
            )
            
            chain = prompt | model
            response = await chain.ainvoke(variables)
            
            return response.content
            
        except Exception as e:
            logger.error(f"Template generation failed: {str(e)}")
            raise
    
    def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings using local sentence-transformers (FREE)
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self._embeddings_model.encode(
                texts,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (FREE)
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self._embeddings_model.encode(
                text,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Single embedding generation failed: {str(e)}")
            raise
    
    async def summarize_text(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """
        Summarize a text passage using Groq
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        template = """Summarize the following text in approximately {max_length} words.
Focus on key points and main ideas.

Text:
{text}

Summary:"""
        
        return await self.generate_with_template(
            template,
            {"text": text[:4000], "max_length": max_length},  # Limit input size
            temperature=0.3
        )
    
    async def extract_key_points(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """
        Extract key points from text using Groq
        
        Args:
            text: Input text
            num_points: Number of key points to extract
            
        Returns:
            List of key points
        """
        template = """Extract {num_points} key points from the following text.
Return only the points as a numbered list.

Text:
{text}

Key Points:"""
        
        response = await self.generate_with_template(
            template,
            {"text": text[:4000], "num_points": num_points},
            temperature=0.3
        )
        
        # Parse numbered list
        points = [
            line.strip().lstrip('0123456789.-) ')
            for line in response.split('\n')
            if line.strip() and any(c.isdigit() for c in line[:3])
        ]
        
        return points[:num_points]
    
    async def classify_intent(
        self,
        query: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """
        Classify query intent into categories using Groq
        
        Args:
            query: Input query
            categories: List of possible categories
            
        Returns:
            Classification result with category and confidence
        """
        template = """Classify the following query into one of these categories: {categories}

Query: {query}

Return your answer in this format:
Category: [chosen category]
Confidence: [high/medium/low]
Reasoning: [brief explanation]"""
        
        response = await self.generate_with_template(
            template,
            {
                "query": query,
                "categories": ", ".join(categories)
            },
            temperature=0.2
        )
        
        # Parse response
        lines = response.split('\n')
        result = {
            "category": "unknown",
            "confidence": "low",
            "reasoning": ""
        }
        
        for line in lines:
            if line.startswith("Category:"):
                result["category"] = line.split(":", 1)[1].strip()
            elif line.startswith("Confidence:"):
                result["confidence"] = line.split(":", 1)[1].strip()
            elif line.startswith("Reasoning:"):
                result["reasoning"] = line.split(":", 1)[1].strip()
        
        return result
    
    async def batch_process(
        self,
        prompts: List[str],
        temperature: float = None
    ) -> List[str]:
        """
        Process multiple prompts in batch
        
        Args:
            prompts: List of prompts
            temperature: Sampling temperature
            
        Returns:
            List of responses
        """
        tasks = [
            self.generate_response(prompt, temperature)
            for prompt in prompts
        ]
        
        return await asyncio.gather(*tasks)
    
    @lru_cache(maxsize=100)
    def get_cached_response(self, prompt: str) -> Optional[str]:
        """Get cached response for a prompt"""
        return None
    
    def clear_cache(self):
        """Clear the response cache"""
        self.get_cached_response.cache_clear()
        logger.info("LLM cache cleared")


# Singleton instance
llm_service = LLMService()


# Helper functions
async def quick_summarize(text: str) -> str:
    """Quick text summarization"""
    return await llm_service.summarize_text(text)


def quick_embed(text: str) -> List[float]:
    """Quick text embedding (synchronous)"""
    return llm_service.generate_embedding(text)


async def quick_classify(query: str, categories: List[str]) -> str:
    """Quick intent classification"""
    result = await llm_service.classify_intent(query, categories)
    return result["category"]