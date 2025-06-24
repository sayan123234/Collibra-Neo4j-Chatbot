import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class Config:
    """Configuration management for Neo4j and Groq connections"""
    
    # Neo4j Configuration
    NEO4J_URL: Optional[str] = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    NEO4J_USERNAME: Optional[str] = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: Optional[str] = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE: Optional[str] = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama3-70b-8192")
    
    # Application Configuration
    MAX_QUERY_RESULTS: int = int(os.getenv("MAX_QUERY_RESULTS", "100"))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", "30"))
    
    # UI Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "Collibra Data Governance Assistant")
    APP_ICON: str = os.getenv("APP_ICON", "🔗")
    APP_VERSION: str = os.getenv("APP_VERSION", "v2.0")
    
    # Sidebar Labels
    SIDEBAR_ASSETS_LABEL: str = os.getenv("SIDEBAR_ASSETS_LABEL", "Assets")
    SIDEBAR_ASSET_TYPES_LABEL: str = os.getenv("SIDEBAR_ASSET_TYPES_LABEL", "Asset Types")
    
    # Sample Questions
    SAMPLE_QUESTIONS: List[str] = [
        "How many assets are in the database?",
        "Show me all data concepts",
        "Who are the technical stewards?",
        "What domains exist in the system?"
    ]
    
    @classmethod
    def validate_neo4j_config(cls) -> bool:
        """Validate Neo4j configuration"""
        missing_vars = []
        if not cls.NEO4J_URL:
            missing_vars.append("NEO4J_URL")
        if not cls.NEO4J_USERNAME:
            missing_vars.append("NEO4J_USERNAME")
        if not cls.NEO4J_PASSWORD:
            missing_vars.append("NEO4J_PASSWORD")
        
        if missing_vars:
            raise ValueError(f"Missing required Neo4j environment variables: {', '.join(missing_vars)}")
        return True
    
    @classmethod
    def validate_groq_config(cls) -> bool:
        """Validate Groq configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("Missing GROQ_API_KEY environment variable")
        return True
    
    @classmethod
    def validate_all(cls) -> bool:
        """Validate all configurations"""
        cls.validate_neo4j_config()
        cls.validate_groq_config()
        return True
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Get configuration summary for debugging"""
        return {
            "neo4j_url": cls.NEO4J_URL,
            "neo4j_username": cls.NEO4J_USERNAME,
            "neo4j_database": cls.NEO4J_DATABASE,
            "groq_model": cls.GROQ_MODEL_NAME,
            "max_results": cls.MAX_QUERY_RESULTS,
            "timeout": cls.QUERY_TIMEOUT,
            "has_neo4j_password": bool(cls.NEO4J_PASSWORD),
            "has_groq_key": bool(cls.GROQ_API_KEY)
        }