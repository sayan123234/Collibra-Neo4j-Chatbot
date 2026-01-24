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

    def check_vector_index_exists(self) -> bool:
        """Check if the vector index exists in Neo4j"""
        if not self.graph:
            raise RuntimeError("GraphService not initialized")

        try:
            result = self.graph.query(
                "SHOW INDEXES WHERE type = 'VECTOR' AND name = $name",
                {"name": settings.VECTOR_INDEX_NAME},
            )
            return len(result) > 0
        except Exception as e:
            logger.warning(f"Could not check vector index: {e}")
            return False

    def semantic_search(
        self, query_embedding: List[float], top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using Neo4j vector index.

        Args:
            query_embedding: The embedding vector for the query
            top_k: Number of results to return (defaults to settings.VECTOR_TOP_K)

        Returns:
            List of nodes with their similarity scores
        """
        if not self.graph:
            raise RuntimeError("GraphService not initialized")

        if top_k is None:
            top_k = settings.VECTOR_TOP_K

        try:
            # Use Neo4j's native vector search with relationship fetching
            results = self.graph.query(
                """
                CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
                YIELD node, score
                OPTIONAL MATCH (node)-[r]-(related)
                WITH node, score, collect(DISTINCT {
                    type: type(r), 
                    target: related.name,
                    label: labels(related)[0]
                })[0..5] as rels
                RETURN 
                    node {.*, labels: labels(node)} as node, 
                    score, 
                    rels
                ORDER BY score DESC
                """,
                {
                    "index_name": settings.VECTOR_INDEX_NAME,
                    "top_k": top_k,
                    "embedding": query_embedding,
                },
            )
            return results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def get_node_with_relationships(self, node_id: str) -> Dict[str, Any]:
        """
        Get a node and its 1-hop relationships for rich context.

        Args:
            node_id: The node's elementId or name

        Returns:
            Dictionary with node properties and relationships
        """
        if not self.graph:
            raise RuntimeError("GraphService not initialized")

        result = self.graph.query(
            """
            MATCH (n) WHERE elementId(n) = $node_id OR n.name = $node_id
            OPTIONAL MATCH (n)-[r]-(related)
            RETURN n {.*, labels: labels(n)} as node,
                   collect(DISTINCT {
                       type: type(r),
                       direction: CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END,
                       target_name: related.name,
                       target_label: labels(related)[0]
                   }) as relationships
            LIMIT 1
            """,
            {"node_id": node_id},
        )

        if result:
            return result[0]
        return {"node": None, "relationships": []}


# Singleton instance
graph_service = GraphService()
