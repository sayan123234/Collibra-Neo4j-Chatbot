import logging
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from backend.app.services.graph_service import graph_service
from backend.app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

# Prompts
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Schema:
{schema}

Conversation History:
{chat_history}

Semantic Context (potentially relevant assets from vector search):
{semantic_context}

The question is:
{question}

Instructions:
1. Use only the provided relationship types and node labels from the schema.
2. For name matching, use CONTAINS or toLower() for case-insensitive partial matching.
   Example: WHERE toLower(n.name) CONTAINS toLower("search term")
3. IMPORTANT: Check the semantic context for exact asset names and use them directly.
4. Do not include any explanations - only output the Cypher query.
5. Use the conversation history to resolve references (e.g., "it", "they", "that asset").
6. Always RETURN meaningful properties like name, not just IDs.

Cypher Query:"""

HYBRID_QA_TEMPLATE = """You are a Data Governance Assistant. Answer the user's question directly and concisely based ONLY on the provided context.

Question: {question}

Context from database:
{cypher_results}

Related assets:
{semantic_results}

Instructions:
1. Answer directly and concisely.
2. STRICTLY BASE YOUR ANSWER ON THE PROVIDED CONTEXT.
3. If the context is empty or irrelevant, say "I couldn't find any information about that in the database."
4. DO NOT invent or halluncinate facts (e.g., do not mention cars, houses, or personal items unless they are in the data).
5. If data is found, state it clearly.

Answer:"""

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
    input_variables=["schema", "question", "chat_history", "semantic_context"],
    template=CYPHER_GENERATION_TEMPLATE,
)

QA_PROMPT = PromptTemplate(
    input_variables=["question", "query", "context"], template=QA_GENERATION_TEMPLATE
)

HYBRID_QA_PROMPT = PromptTemplate(
    input_variables=["question", "cypher_results", "semantic_results"],
    template=HYBRID_QA_TEMPLATE,
)

ROUTING_TEMPLATE = """Task: Classify the user input into one of two categories: 'database' or 'general'.

Input: {question}

Categories:
- 'database': The user is asking about data, assets, ownership, definitions, or follow-up questions like "what else?", "show me more", or "who owns that?".
- 'general': The user is ONLY greeting (e.g., "hi", "hello"), asking "how are you", or checking system status without referencing data.

Instructions:
1. If the question implies looking up information (even vaguely like "what about Bob?"), classify as 'database'.
2. Return ONLY the category name ('database' or 'general').
3. Do not explain.

Category:"""

ROUTING_PROMPT = PromptTemplate(input_variables=["question"], template=ROUTING_TEMPLATE)

GENERAL_CHAT_TEMPLATE = """You are a helpful Data Governance Assistant for Collibra.
Input: {question}

Instructions:
1. Answer greetings and small talk professionally.
2. If the user asks for specific data (e.g., "What does Bob own?"), do NOT answer it here. Instead, say "Let me check the database for you" or similar, so the system knows to route it to the database.
3. Never invent data governance assets or user properties.

Answer:"""

GENERAL_CHAT_PROMPT = PromptTemplate(
    input_variables=["question"], template=GENERAL_CHAT_TEMPLATE
)


class ChatService:
    def __init__(self):
        self.graph_service = graph_service
        self.embedding_service = embedding_service

    def _perform_semantic_search(self, question: str) -> List[Dict[str, Any]]:
        """Perform semantic search and return formatted results"""
        try:
            query_embedding = self.embedding_service.embed_query(question)
            results = self.graph_service.semantic_search(query_embedding)
            return results
        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            return []

    def _format_semantic_context(self, semantic_results: List[Dict[str, Any]]) -> str:
        """Format semantic results for prompt context"""
        if not semantic_results:
            return "No relevant assets found."

        context_parts = []
        for i, result in enumerate(semantic_results[:5], 1):
            node = result.get("node", {})
            score = result.get("score", 0)
            rels = result.get("rels", [])
            name = node.get("name", "Unknown")
            labels = node.get("labels", ["Unknown"])
            asset_type = labels[0] if labels else "Unknown"
            description = node.get("Description", node.get("definition", ""))[:100]

            # Format relationships
            rel_str = ""
            if rels:
                rel_parts = [
                    f"{r['target']} ({r['type'].replace('_', ' ')})"
                    for r in rels
                    if r.get("target")
                ]
                if rel_parts:
                    rel_str = "\n   Connections: " + ", ".join(rel_parts)

            context_parts.append(
                f"{i}. {name} ({asset_type}) [similarity: {score:.2f}]"
                + (f" - {description}..." if description else "")
                + rel_str
            )

        return "\n".join(context_parts)

    async def process_question(
        self, question: str, history: List[Dict[str, str]] = []
    ) -> Dict[str, Any]:
        """Process a natural language question with hybrid RAG"""
        if not self.graph_service.graph:
            self.graph_service.connect()

        try:
            # Format history string
            history_str = ""
            for msg in history[-5:]:
                history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

            # 0. Routing Step
            routing_response = self.graph_service.llm.invoke(
                ROUTING_PROMPT.format(question=question)
            )
            category = routing_response.content.strip().lower()

            if "general" in category:
                response = self.graph_service.llm.invoke(
                    GENERAL_CHAT_PROMPT.format(question=question)
                )
                return {
                    "question": question,
                    "answer": response.content.strip(),
                    "cypher_query": None,
                    "results": None,
                }

            # 1. Semantic Search (Parallel context gathering)
            semantic_results = self._perform_semantic_search(question)
            semantic_context = self._format_semantic_context(semantic_results)

            # 2. Generate Cypher with semantic context
            schema = self.graph_service.get_schema()
            cypher_response = self.graph_service.llm.invoke(
                CYPHER_PROMPT.format(
                    schema=schema,
                    question=question,
                    chat_history=history_str,
                    semantic_context=semantic_context,
                )
            )
            cypher_query = self._clean_cypher(cypher_response.content)

            # 3. Execute Cypher Query
            if "LIMIT" not in cypher_query.upper() and "RETURN" in cypher_query.upper():
                cypher_query += " LIMIT 50"

            cypher_results = []
            try:
                cypher_results = self.graph_service.execute_cypher(cypher_query)
            except Exception as e:
                logger.warning(f"Cypher execution failed: {e}")

            # 4. Generate Hybrid Answer
            if not cypher_results and not semantic_results:
                answer = "No data found matching your query."
            else:
                # Format results for LLM
                cypher_str = (
                    str(cypher_results[:20])
                    if cypher_results
                    else "No structured results."
                )
                semantic_str = self._format_semantic_context(semantic_results)

                qa_response = self.graph_service.llm.invoke(
                    HYBRID_QA_PROMPT.format(
                        question=question,
                        cypher_results=cypher_str,
                        semantic_results=semantic_str,
                    )
                )
                answer = qa_response.content.strip()

            return {
                "question": question,
                "cypher_query": cypher_query,
                "results": cypher_results,
                "semantic_results": [
                    {"name": r.get("node", {}).get("name"), "score": r.get("score")}
                    for r in semantic_results[:5]
                ],
                "answer": answer,
            }

        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {"question": question, "error": str(e)}

    def _clean_cypher(self, text: str) -> str:
        """Clean LLM response to get just the Cypher query"""
        text = text.replace("```cypher", "").replace("```", "").strip()
        return text


chat_service = ChatService()
