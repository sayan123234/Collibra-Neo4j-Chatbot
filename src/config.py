import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class Config:
    """Configuration management for Neo4j and Groq connections"""
    
    # Neo4j Configuration
    NEO4J_URL = os.getenv("NEO4J_URL")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
    
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
    
    @classmethod
    def validate_neo4j_config(cls):
        """Validate Neo4j configuration"""
        required_fields = [cls.NEO4J_URL, cls.NEO4J_USERNAME, cls.NEO4J_PASSWORD]
        if not all(required_fields):
            raise ValueError("Missing required Neo4j environment variables")
        return True
    
    @classmethod
    def validate_groq_config(cls):
        """Validate Groq configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("Missing GROQ_API_KEY environment variable")
        return True