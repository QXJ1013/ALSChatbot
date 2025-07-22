from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ALS Semantic Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API keys
    # HF_API_TOKEN="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"
    # HF_MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.2"
    # OPENAI_API_KEY: Optional[str] = None  
    IBM_GRANITE_API_KEY: str
    IBM_GRANITE_API_URL: str = "https://api.us-south.ml.cloud.ibm.com"

    # Database configuration
    DATABASE_URL: str = "postgresql://user:pass@localhost/als_db"
    REDIS_URL: str = "redis://localhost:6379"

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Vector database settings (e.g., Chroma)
    CHROMA_HOST: Optional[str] = "localhost"
    CHROMA_PORT: Optional[int] = 8000

    # Prompt configuration
    PROMPT_PATH: str = "./prompts"
    DEFAULT_LANGUAGE: str = "en"

    class Config:
        env_file = ".env"


settings = Settings()
