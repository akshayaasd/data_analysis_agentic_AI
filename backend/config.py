"""
Configuration management for the agentic data analysis system.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # LLM Configuration
    default_llm_provider: str = "groq"  # groq, openai, anthropic
    default_model: str = "llama-3.3-70b-versatile"  # For Groq
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # Agent Configuration
    max_agent_steps: int = 10
    agent_timeout: int = 120  # seconds
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    vector_db_path: str = "./data/chromadb"
    
    # File Storage
    upload_dir: str = "./data/uploads"
    plots_dir: str = "./data/plots"
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.plots_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.database_url.replace("sqlite+aiosqlite:///", "")), exist_ok=True)
