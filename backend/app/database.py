from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import AsyncGenerator
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cost_optimizer")
    database_url_sync: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cost_optimizer").replace("+asyncpg", "")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API
    api_v1_prefix: str = "/api/v1"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Cloud providers
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    gcp_credentials_path: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
    
    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")
    azure_client_secret: str = os.getenv("AZURE_CLIENT_SECRET", "")
    azure_subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        # Load environment-specific file
        env_file = [
            ".env.local" if os.getenv("ENVIRONMENT") != "docker" else ".env.docker",
            ".env",  # fallback
        ]
        extra = "allow"  # Allow extra fields

# Global settings instance
settings = Settings()

# Database engine
engine = create_async_engine(settings.database_url, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
