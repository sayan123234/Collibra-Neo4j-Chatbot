from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Neo4j Configuration
    NEO4J_URL: str = Field(default="bolt://localhost:7687")
    NEO4J_USERNAME: str = Field(default="neo4j")
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = Field(default="neo4j")

    # Groq Configuration
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str = Field(default="llama-3.3-70b-versatile")

    # Application Configuration
    MAX_QUERY_RESULTS: int = Field(default=100)
    QUERY_TIMEOUT: int = Field(default=30)

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Collibra Neo4j Chatbot"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
