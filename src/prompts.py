from langchain_core.prompts import PromptTemplate

# Cypher generation prompt - focused and strict
CYPHER_GENERATION_TEMPLATE = """You are a Neo4j Cypher expert. Generate ONLY a valid Cypher query.

Schema:
{schema}

Rules:
1. Output ONLY the Cypher query - no explanations, no markdown, no additional text
2. Use only the node labels, relationship types, and properties shown in the schema
3. Start your response directly with MATCH, RETURN, CREATE, etc.

Question: {question}

Cypher Query:"""

# Answer generation prompt - clear and direct
QA_GENERATION_TEMPLATE = """You are an assistant that answers questions based on database query results.

Question: {question}
Cypher Query: {query}
Query Results: {context}

Instructions:
1. Use the query results to answer the question directly
2. If results contain data, present it clearly
3. Format the answer in a user-friendly way
4. Don't say "I don't know" if there are actual results

Answer:"""

# Create prompt templates
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
qa_prompt = PromptTemplate.from_template(QA_GENERATION_TEMPLATE)