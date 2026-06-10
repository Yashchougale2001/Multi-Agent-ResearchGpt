# from pydantic_settings import BaseSettings
# from typing import List
# import os

# class Settings(BaseSettings):
#     # Groq Configuration (FREE)
#     GROQ_API_KEY: str
#     GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Fast and free
    
#     # Embedding Model (Local - FREE)
#     EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
#     # ChromaDB
#     CHROMA_PERSIST_DIR: str = "./chroma_db"
#     CHROMA_COLLECTION_NAME: str = "research_docs"
    
#     # Redis
#     REDIS_URL: str = "redis://localhost:6379"
    
#     # API Configuration
#     API_HOST: str = "0.0.0.0"
#     API_PORT: int = 8000
#     CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
#     # Research Settings
#     MAX_SEARCH_RESULTS: int = 10
#     MAX_SUBTASKS: int = 5
#     RETRIEVAL_TOP_K: int = 5
#     MAX_TOKENS: int = 8000
#     TEMPERATURE: float = 0.7
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = True

# settings = Settings()
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Groq Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "research_docs"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Research Settings
    MAX_SEARCH_RESULTS: int = 10
    MAX_SUBTASKS: int = 5
    RETRIEVAL_TOP_K: int = 5
    MAX_TOKENS: int = 8000
    TEMPERATURE: float = 0.7

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()