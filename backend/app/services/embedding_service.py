"""
Embedding Service for Hybrid RAG

Uses sentence-transformers to generate embeddings for semantic search.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Lazy loading to avoid import overhead if not used
_model = None


def get_embedding_model():
    """Lazy load the embedding model"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from backend.app.core.config import settings

        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for a single text string.

    Args:
        text: The text to embed

    Returns:
        List of floats representing the embedding vector
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch processing).

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return [e.tolist() for e in embeddings]


def format_node_for_embedding(node: dict, relationships: List[dict] = None) -> str:
    """
    Format a node and its relationships into a rich text for embedding.

    Args:
        node: Dictionary with node properties (must have 'name' and 'labels')
        relationships: Optional list of relationship dicts with 'type' and 'target_name'

    Returns:
        Formatted text suitable for embedding
    """
    parts = []

    # Name and type
    name = node.get("name", node.get("Display_Name", "Unknown"))
    labels = node.get("labels", ["Unknown"])
    asset_type = labels[0] if labels else "Unknown"
    parts.append(f"{name} ({asset_type.replace('_', ' ')})")

    # Key properties
    key_props = ["Domain", "Description", "Status", "definition", "Community"]
    for prop in key_props:
        if prop in node and node[prop]:
            parts.append(f"{prop}: {node[prop]}")

    # Owner information
    owner = node.get("Created_By") or node.get("Owner")
    if owner:
        parts.append(f"Owner: {owner}")

    # 1-hop relationships (connected assets)
    if relationships:
        rel_summary = []
        for rel in relationships[:10]:  # Limit to prevent very long embeddings
            if rel is None:
                continue
            rel_type = (rel.get("type") or "").replace("_", " ")
            target = rel.get("target_name") or "Unknown"
            if target != "Unknown":
                rel_summary.append(f"{target} ({rel_type})")

        if rel_summary:
            parts.append(f"Connected to: {', '.join(rel_summary)}")

    return "\n".join(parts)


class EmbeddingService:
    """Service class for embedding operations"""

    def __init__(self):
        self._initialized = False

    def initialize(self):
        """Pre-load the model (call during app startup)"""
        if not self._initialized:
            get_embedding_model()
            self._initialized = True

    def embed_query(self, query: str) -> List[float]:
        """Embed a user query"""
        return embed_text(query)

    def embed_node(self, node: dict, relationships: List[dict] = None) -> List[float]:
        """Embed a node with its context"""
        text = format_node_for_embedding(node, relationships)
        return embed_text(text)

    def embed_nodes_batch(self, nodes_with_rels: List[tuple]) -> List[List[float]]:
        """
        Batch embed multiple nodes.

        Args:
            nodes_with_rels: List of (node_dict, relationships_list) tuples

        Returns:
            List of embedding vectors
        """
        texts = [
            format_node_for_embedding(node, rels) for node, rels in nodes_with_rels
        ]
        return embed_texts(texts)


# Singleton instance
embedding_service = EmbeddingService()
