import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    mongodb_uri: str = os.getenv("MONGODB_URI", "")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "multiagent_rag")
    mongodb_api_user: str = os.getenv("MONGODB_API_USER", "")
    mongodb_api_password: str = os.getenv("MONGODB_API_PASSWORD", "")
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langchain_tracing_v2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "multiagent-rag-app")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    port: int = int(os.environ.get("PORT", "8080"))

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
