from .graph_service import GraphService
from .prompts import cypher_prompt, qa_prompt

class NLToCypherQuery:
    """Natural Language to Cypher Query System - Most Robust Implementation"""
    
    def __init__(self):
        self.graph_service = GraphService()
        print("NL to Cypher Query System initialized!\n")
    
    def query(self, question):
        """Main query method - processes natural language question and returns answer"""
        try:
            print(f"\nQuestion: {question}")
            
            # Step 1: Generate Cypher query
            cypher_query = self._generate_cypher(question)
            print(f"\nGenerated Cypher: {cypher_query}")
            
            # Step 2: Execute Cypher query
            query_results = self._execute_query(cypher_query)
            print(f"\nQuery Results: {query_results}")
            
            # Step 3: Generate natural language answer
            answer = self._generate_answer(question, cypher_query, query_results)
            print(f"\n\nAnswer: {answer}\n")
            
            return {
                "question": question,
                "cypher_query": cypher_query,
                "query_results": query_results,
                "answer": answer
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def _generate_cypher(self, question):
        """Generate Cypher query from natural language question"""
        cypher_input = {
            "schema": self.graph_service.get_schema(),
            "question": question
        }
        
        cypher_response = self.graph_service.llm.invoke(cypher_prompt.format(**cypher_input))
        return cypher_response.content.strip()
    
    def _execute_query(self, cypher_query):
        """Execute the Cypher query"""
        results = self.graph_service.execute_cypher(cypher_query)
        return results if results is not None else []
    
    def _generate_answer(self, question, cypher_query, query_results):
        """Generate natural language answer from query results"""
        if not query_results:
            return "No data found for your query."
        
        # For simple single-value results, format directly
        if len(query_results) == 1 and len(query_results[0]) == 1:
            key, value = list(query_results[0].items())[0]
            field_name = key.split('.')[-1] if '.' in key else key
            return f"The {field_name} is: {value}"
        
        # For complex results, use LLM to generate answer
        qa_input = {
            "question": question,
            "query": cypher_query,
            "context": str(query_results)
        }
        
        answer_response = self.graph_service.llm.invoke(qa_prompt.format(**qa_input))
        return answer_response.content.strip()
    
    def get_schema_info(self):
        """Get and display graph schema information"""
        schema = self.graph_service.get_schema()
        print("Graph Schema:")
        print(schema)
        return schema
    
    def test_connection(self):
        """Test the graph connection"""
        return self.graph_service.test_connection()