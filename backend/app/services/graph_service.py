import logging
from typing import Optional, List, Dict, Any
from langchain_neo4j import Neo4jGraph
from langchain_groq import ChatGroq
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self):
        self.graph: Optional[Neo4jGraph] = None
        self.llm: Optional[ChatGroq] = None
        self._schema_cache: Optional[str] = None

    def connect(self):
        """Initialize Neo4j and Groq connections"""
        try:
            self.graph = Neo4jGraph(
                url=settings.NEO4J_URL,
                username=settings.NEO4J_USERNAME,
                password=settings.NEO4J_PASSWORD,
                database=settings.NEO4J_DATABASE,
                timeout=settings.QUERY_TIMEOUT,
            )

            self.llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL_NAME,
                temperature=0,
                max_tokens=4096,
                timeout=settings.QUERY_TIMEOUT,
            )
            logger.info("GraphService connections initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize GraphService: {e}")
            raise

    def close(self):
        """Close connections"""
        if self.graph:
            # Neo4jGraph doesn't always have a close method depending on version,
            # but usually it manages its own driver.
            # If we needed to close the driver explicitly we would access self.graph._driver.close()
            # but strictly speaking langchain wrapper handles it.
            pass

    def get_schema(self) -> str:
        if not self.graph:
            raise RuntimeError("GraphService not initialized")

        if self._schema_cache is None:
            self.graph.refresh_schema()
            self._schema_cache = self.graph.schema
        return self._schema_cache

    def refresh_schema(self) -> str:
        if not self.graph:
            raise RuntimeError("GraphService not initialized")
        self.graph.refresh_schema()
        self._schema_cache = self.graph.schema
        return self._schema_cache

    def execute_cypher(self, query: str) -> List[Dict[str, Any]]:
        if not self.graph:
            raise RuntimeError("GraphService not initialized")
        return self.graph.query(query)

    def validate_cypher(self, query: str) -> Dict[str, Any]:
        if not self.graph:
            raise RuntimeError("GraphService not initialized")
        try:
            self.graph.query(f"EXPLAIN {query}")
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "error": str(e)}


# Singleton instance
graph_service = GraphService()
