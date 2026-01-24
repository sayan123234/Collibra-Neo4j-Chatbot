import logging
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from backend.app.services.graph_service import graph_service

logger = logging.getLogger(__name__)

# Prompts (moved from src/prompts.py concept)
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Schema:
{schema}

Conversation History:
{chat_history}

The question is:
{question}

Instructions:
1. Use only the provided relationship types and node labels.
2. Do not use any other relationship types or node labels that are not provided.
3. Schema is provided in the format of Node properties and Relationships.
4. Do not include any explanations or apologies in your responses.
5. Do not include any text except the generated Cypher statement.
6. Use the existing schema to understand the graph structure.
7. Use the conversation history to resolve references (e.g., "it", "they", "that asset").

Cypher Query:"""

QA_GENERATION_TEMPLATE = """Task: Generate a natural language answer from the given query results.
Question: {question}
Query: {query}
Results: {context}

Instructions:
1. Answer the question based ONLY on the results provided.
2. If the results are empty, state that no information was found.
3. Be concise and professional.
4. If the results contain a count, state it clearly.
5. If the results contain a list, summarize it if it's long.

Answer:"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "chat_history"],
    template=CYPHER_GENERATION_TEMPLATE,
)

QA_PROMPT = PromptTemplate(
    input_variables=["question", "query", "context"], template=QA_GENERATION_TEMPLATE
)

ROUTING_TEMPLATE = """Task: Classify the user input into one of two categories: 'database' or 'general'.

Input: {question}

Categories:
- 'database': The user is asking for information, counts, relationships, or details about data assets, domains, users, or the graph structure.
- 'general': The user is greeting, asking "how are you", or making small talk that requires no database access.

Instructions:
1. Return ONLY the category name ('database' or 'general').
2. Do not explain.

Category:"""

ROUTING_PROMPT = PromptTemplate(input_variables=["question"], template=ROUTING_TEMPLATE)

GENERAL_CHAT_TEMPLATE = """You are a helpful Data Governance Assistant for Collibra.
Input: {question}
Answer the user in a friendly, professional manner. Do not mention Cypher or databases unless asked.
Answer:"""

GENERAL_CHAT_PROMPT = PromptTemplate(
    input_variables=["question"], template=GENERAL_CHAT_TEMPLATE
)


class ChatService:
    def __init__(self):
        self.graph_service = graph_service

    async def process_question(
        self, question: str, history: List[Dict[str, str]] = []
    ) -> Dict[str, Any]:
        """Process a natural language question with history"""
        if not self.graph_service.graph:
            # Try to connect if not connected (lazy init or reconnection)
            # In production, we'd rely on startup event, but this adds robustness
            self.graph_service.connect()

        try:
            # Format history string
            history_str = ""
            for msg in history[-5:]:  # Limit to last 5 messages
                history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

            # 0. Routing Step
            routing_response = self.graph_service.llm.invoke(
                ROUTING_PROMPT.format(question=question)
            )
            category = routing_response.content.strip().lower()

            if "general" in category:
                # Handle general chat directly
                response = self.graph_service.llm.invoke(
                    GENERAL_CHAT_PROMPT.format(question=question)
                )
                return {
                    "question": question,
                    "answer": response.content.strip(),
                    "cypher_query": None,
                    "results": None,
                }

            # 1. Generate Cypher (Database Query)
            schema = self.graph_service.get_schema()
            cypher_response = self.graph_service.llm.invoke(
                CYPHER_PROMPT.format(
                    schema=schema, question=question, chat_history=history_str
                )
            )
            cypher_query = self._clean_cypher(cypher_response.content)

            # 2. Execute Query
            # Safety: Add LIMIT if missing
            if "LIMIT" not in cypher_query.upper() and "RETURN" in cypher_query.upper():
                cypher_query += " LIMIT 50"

            results = self.graph_service.execute_cypher(cypher_query)

            # 3. Generate Answer
            if not results:
                answer = "No data found matching your query."
            else:
                qa_response = self.graph_service.llm.invoke(
                    QA_PROMPT.format(
                        question=question,
                        query=cypher_query,
                        context=str(results[:20]),  # Limit context size
                    )
                )
                answer = qa_response.content.strip()

            return {
                "question": question,
                "cypher_query": cypher_query,
                "results": results,
                "answer": answer,
            }

        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {"question": question, "error": str(e)}

    def _clean_cypher(self, text: str) -> str:
        """Clean LLM response to get just the Cypher query"""
        # Remove markdown code blocks
        text = text.replace("```cypher", "").replace("```", "").strip()
        return text


chat_service = ChatService()
