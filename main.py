from src.nl_to_cypher import NLToCypherQuery

def main():
    """Main application entry point"""
    try:
        # Initialize the query system
        query_system = NLToCypherQuery()
        
        # Test connection
        if not query_system.test_connection():
            print("Failed to connect to Neo4j. Please check your configuration.")
            return
        
        # Interactive mode
        print("Natural Language to Cypher Query System")
        print("Type 'quit' to exit, 'schema' to view graph schema")
        print("-" * 50)
        
        while True:
            try:
                user_question = input("\nEnter your question: ").strip()
                
                if user_question.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_question.lower() == 'schema':
                    query_system.get_schema_info()
                    continue
                
                if user_question:
                    query_system.query(user_question)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    except Exception as e:
        print(f"Application error: {e}")
        print("Please check your environment variables and database connection.")

if __name__ == "__main__":
    main()