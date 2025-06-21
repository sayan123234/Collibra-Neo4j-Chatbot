from langchain_neo4j import Neo4jGraph
from langchain_groq import ChatGroq
from .config import Config

class GraphService:
    """Service class for Neo4j graph operations"""
    
    def __init__(self):
        # Validate configuration
        Config.validate_neo4j_config()
        Config.validate_groq_config()
        
        # Initialize Neo4j connection
        self.graph = Neo4jGraph(
            url=Config.NEO4J_URL,
            username=Config.NEO4J_USERNAME,
            password=Config.NEO4J_PASSWORD,
            database=Config.NEO4J_DATABASE
        )
        
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
            model_name=Config.GROQ_MODEL_NAME,
            temperature=0
        )
        
        print("Neo4j and Groq connections initialized successfully!")
    
    def get_schema(self):
        """Get the graph schema"""
        return self.graph.schema
    
    def execute_cypher(self, cypher_query):
        """Execute a Cypher query and return results"""
        try:
            return self.graph.query(cypher_query)
        except Exception as e:
            print(f"Error executing Cypher query: {e}")
            return None
    
    def test_connection(self):
        """Test the graph connection"""
        try:
            result = self.graph.query("MATCH (n) RETURN count(n) as node_count LIMIT 1")
            print(f"Connection test successful. Node count: {result}")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False