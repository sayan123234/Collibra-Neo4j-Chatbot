import logging
from typing import Optional, Dict, Any, List
from langchain_neo4j import Neo4jGraph
from langchain_groq import ChatGroq
from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphService:
    """Enhanced service class for Neo4j graph operations with improved error handling and performance"""
    
    def __init__(self):
        self.graph: Optional[Neo4jGraph] = None
        self.llm: Optional[ChatGroq] = None
        self._schema_cache: Optional[str] = None
        self._initialize_connections()
    
    def _initialize_connections(self) -> None:
        """Initialize Neo4j and Groq connections with proper error handling"""
        try:
            # Validate configuration
            Config.validate_all()
            
            # Initialize Neo4j connection with enhanced settings
            self.graph = Neo4jGraph(
                url=Config.NEO4J_URL,
                username=Config.NEO4J_USERNAME,
                password=Config.NEO4J_PASSWORD,
                database=Config.NEO4J_DATABASE,
                timeout=Config.QUERY_TIMEOUT
            )
            
            # Initialize LLM with optimized settings
            self.llm = ChatGroq(
                groq_api_key=Config.GROQ_API_KEY,
                model_name=Config.GROQ_MODEL_NAME,
                temperature=0,
                max_tokens=4096,
                timeout=30
            )
            
            logger.info("Neo4j and Groq connections initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise
    
    def get_schema(self) -> str:
        """Get the graph schema with caching for performance"""
        if self._schema_cache is None:
            try:
                self._schema_cache = self.graph.schema
                logger.info("Schema cached successfully")
            except Exception as e:
                logger.error(f"Error fetching schema: {e}")
                raise
        return self._schema_cache
    
    def refresh_schema(self) -> str:
        """Force refresh the schema cache"""
        self._schema_cache = None
        return self.get_schema()
    
    def execute_cypher(self, cypher_query: str) -> Optional[List[Dict[str, Any]]]:
        """Execute a Cypher query with enhanced error handling and result limiting"""
        if not cypher_query or not cypher_query.strip():
            logger.warning("Empty Cypher query provided")
            return None
        
        try:
            # Add LIMIT clause if not present to prevent large result sets
            if "LIMIT" not in cypher_query.upper() and "RETURN" in cypher_query.upper():
                cypher_query = f"{cypher_query} LIMIT {Config.MAX_QUERY_RESULTS}"
            
            logger.info(f"Executing Cypher query: {cypher_query[:100]}...")
            result = self.graph.query(cypher_query)
            logger.info(f"Query executed successfully, returned {len(result) if result else 0} results")
            return result
            
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            logger.error(f"Query: {cypher_query}")
            return None
    
    def test_connection(self) -> bool:
        """Test the graph connection with detailed diagnostics"""
        try:
            # Test basic connectivity
            result = self.graph.query("MATCH (n) RETURN count(n) as node_count LIMIT 1")
            node_count = result[0]['node_count'] if result else 0
            
            # Test LLM connectivity
            test_response = self.llm.invoke("Test connection")
            
            logger.info(f"Connection test successful. Node count: {node_count}")
            logger.info(f"LLM test response received: {len(test_response.content)} characters")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    def execute_cypher_paginated(self, cypher_query: str, page_size: int = 50, page: int = 1) -> Dict[str, Any]:
        """Execute Cypher query with pagination"""
        offset = (page - 1) * page_size
        
        # Add pagination to query
        if "LIMIT" not in cypher_query.upper():
            paginated_query = f"{cypher_query} SKIP {offset} LIMIT {page_size}"
        else:
            # Replace existing LIMIT with pagination
            import re
            paginated_query = re.sub(r'LIMIT\s+\d+', f'SKIP {offset} LIMIT {page_size}', cypher_query, flags=re.IGNORECASE)
        
        # Get total count
        count_query = f"MATCH {cypher_query.split('RETURN')[0].split('MATCH')[1]} RETURN count(*) as total"
        
        results = self.graph.query(paginated_query)
        try:
            total_count = self.graph.query(count_query)[0]['total']
        except:
            total_count = len(results)
        
        return {
            "results": results,
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        try:
            queries = {
                "node_count": "MATCH (n) RETURN count(n) as count",
                "relationship_count": "MATCH ()-[r]->() RETURN count(r) as count",
                "node_labels": "CALL db.labels() YIELD label RETURN collect(label) as labels",
                "relationship_types": "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
            }
            
            info = {}
            for key, query in queries.items():
                try:
                    result = self.graph.query(query)
                    if key in ["node_labels", "relationship_types"]:
                        info[key] = result[0][key.split('_')[0] + 's'] if result else []
                    else:
                        info[key] = result[0]['count'] if result else 0
                except Exception as e:
                    logger.warning(f"Failed to get {key}: {e}")
                    info[key] = "Unknown"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
    
    def validate_cypher_syntax(self, cypher_query: str) -> Dict[str, Any]:
        """Validate Cypher query syntax without executing it"""
        try:
            # Use EXPLAIN to validate syntax without execution
            explain_query = f"EXPLAIN {cypher_query}"
            self.graph.query(explain_query)
            return {"valid": True, "message": "Query syntax is valid"}
        except Exception as e:
            return {"valid": False, "message": str(e)}
    
    def close_connections(self) -> None:
        """Properly close all connections"""
        try:
            if self.graph:
                self.graph.close()
                logger.info("Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")