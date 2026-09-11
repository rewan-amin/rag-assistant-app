import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    VECTOR_STORE_PATH: str = "./data/vector_store"
    COLLECTION_NAME: str = "documents"
    EMBEDDING_MODEL_NAME: str = "futur/Qwen3-Embedding-0.6B-model2vec-onnx"
    TOP_K: int = 5
    CORS_ORIGINS: str = "http://localhost:8501"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
