from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Document Assistant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "company_documents"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    top_k: int = 4
    llm_provider: str = "none"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    frankfurter_base_url: str = "https://api.frankfurter.app"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
