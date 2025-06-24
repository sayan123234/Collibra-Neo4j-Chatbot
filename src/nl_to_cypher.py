import logging
from typing import Dict, Any, List, Optional
from .graph_service import GraphService
from .prompts import cypher_prompt, qa_prompt, validation_prompt

# Configure logging
logger = logging.getLogger(__name__)

class NLToCypherQuery:
    """Enhanced Natural Language to Cypher Query System with improved error handling and performance"""
    
    def __init__(self):
        self.graph_service = GraphService()
        self._query_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("NL to Cypher Query System initialized!")
    
    def query(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """Main query method - processes natural language question and returns answer"""
        if not question or not question.strip():
            return {"error": "Empty question provided"}
        
        question = question.strip()
        
        # Check cache first
        if use_cache and question in self._query_cache:
            logger.info(f"Returning cached result for: {question[:50]}...")
            return self._query_cache[question]
        
        try:
            logger.info(f"Processing question: {question}")
            
            # Step 1: Generate Cypher query
            cypher_query = self._generate_cypher(question)
            if not cypher_query:
                return {"error": "Failed to generate Cypher query"}
            
            logger.info(f"Generated Cypher: {cypher_query}")
            
            # Step 2: Validate Cypher syntax (optional)
            validation_result = self._validate_cypher(cypher_query)
            if not validation_result.get("valid", True):
                logger.warning(f"Cypher validation warning: {validation_result.get('message', 'Unknown issue')}")
            
            # Step 3: Execute Cypher query
            query_results = self._execute_query(cypher_query)
            logger.info(f"Query returned {len(query_results) if query_results else 0} results")
            
            # Step 4: Generate natural language answer
            answer = self._generate_answer(question, cypher_query, query_results)
            logger.info(f"Generated answer: {answer[:100]}...")
            
            result = {
                "question": question,
                "cypher_query": cypher_query,
                "query_results": query_results,
                "answer": answer,
                "validation": validation_result
            }
            
            # Cache the result
            if use_cache:
                self._query_cache[question] = result
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg, "question": question}
    
    def _generate_cypher(self, question: str) -> Optional[str]:
        """Generate Cypher query from natural language question with enhanced error handling"""
        try:
            cypher_input = {
                "schema": self.graph_service.get_schema(),
                "question": question
            }
            
            cypher_response = self.graph_service.llm.invoke(cypher_prompt.format(**cypher_input))
            cypher_query = cypher_response.content.strip()
            
            # Clean up the response (remove markdown, extra text)
            cypher_query = self._clean_cypher_response(cypher_query)
            
            return cypher_query
            
        except Exception as e:
            logger.error(f"Error generating Cypher query: {e}")
            return None
    
    def _clean_cypher_response(self, cypher_query: str) -> str:
        """Clean up the Cypher query response from LLM"""
        # Remove markdown code blocks
        if "```" in cypher_query:
            lines = cypher_query.split('\n')
            cypher_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (not in_code_block and line.strip().upper().startswith(('MATCH', 'RETURN', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE', 'WITH', 'UNWIND', 'CALL'))):
                    cypher_lines.append(line)
            
            cypher_query = '\n'.join(cypher_lines).strip()
        
        # Remove any explanatory text before the query
        lines = cypher_query.split('\n')
        cypher_lines = []
        found_cypher = False
        
        for line in lines:
            if line.strip().upper().startswith(('MATCH', 'RETURN', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE', 'WITH', 'UNWIND', 'CALL')):
                found_cypher = True
            if found_cypher:
                cypher_lines.append(line)
        
        return '\n'.join(cypher_lines).strip() if cypher_lines else cypher_query.strip()
    
    def _validate_cypher(self, cypher_query: str) -> Dict[str, Any]:
        """Validate Cypher query syntax"""
        try:
            return self.graph_service.validate_cypher_syntax(cypher_query)
        except Exception as e:
            logger.warning(f"Cypher validation failed: {e}")
            return {"valid": False, "message": str(e)}
    
    def _execute_query(self, cypher_query: str) -> List[Dict[str, Any]]:
        """Execute the Cypher query with enhanced error handling"""
        try:
            results = self.graph_service.execute_cypher(cypher_query)
            return results if results is not None else []
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def _generate_answer(self, question: str, cypher_query: str, query_results: List[Dict[str, Any]]) -> str:
        """Generate natural language answer from query results with improved formatting"""
        try:
            if not query_results:
                return "No data found matching your query. The database might not contain the requested information, or the query might need to be refined."
            
            # For simple single-value results, format directly
            if len(query_results) == 1 and len(query_results[0]) == 1:
                key, value = list(query_results[0].items())[0]
                field_name = key.split('.')[-1] if '.' in key else key
                return f"The **{field_name}** is: **{value}**"
            
            # For count queries
            if len(query_results) == 1 and any('count' in str(k).lower() for k in query_results[0].keys()):
                count_key = next(k for k in query_results[0].keys() if 'count' in str(k).lower())
                count_value = query_results[0][count_key]
                return f"Found **{count_value}** items matching your query."
            
            # For complex results, use LLM to generate answer
            qa_input = {
                "question": question,
                "query": cypher_query,
                "context": str(query_results[:20])  # Limit context to prevent token overflow
            }
            
            answer_response = self.graph_service.llm.invoke(qa_prompt.format(**qa_input))
            return answer_response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Found {len(query_results)} results, but encountered an error formatting the response: {str(e)}"
    
    def get_schema_info(self) -> str:
        """Get and display graph schema information"""
        try:
            schema = self.graph_service.get_schema()
            logger.info("Retrieved graph schema")
            return schema
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return f"Error retrieving schema: {str(e)}"
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        return self.graph_service.get_database_info()
    
    def test_connection(self) -> bool:
        """Test the graph connection"""
        return self.graph_service.test_connection()
    
    def clear_cache(self) -> None:
        """Clear the query cache"""
        self._query_cache.clear()
        logger.info("Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_queries": len(self._query_cache),
            "cache_keys": list(self._query_cache.keys())
        }