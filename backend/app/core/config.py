from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "Legal Document Search & Analysis"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./legal_docs.db"
    
    # Vector Database Configuration  
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "legal_documents"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # AI Model Configuration
    DOCUMENT_ANALYSIS_MODEL: str = "anthropic/claude-3-sonnet"
    REASONING_MODEL: str = "anthropic/claude-3-opus"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    
    # Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_TOKENS_PER_CHUNK: int = 512
    
    # Search Configuration
    DEFAULT_SEARCH_RESULTS: int = 10
    MAX_SEARCH_RESULTS: int = 50
    
    # Redis Configuration (for caching and queues)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Elasticsearch Configuration
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "legal_documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 