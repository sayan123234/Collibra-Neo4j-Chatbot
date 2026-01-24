"""
Vector Index Setup Script

Run this script to:
1. Create a vector index in Neo4j (if not exists)
2. Generate embeddings for nodes
3. Store embeddings in the vector index

Usage:
    # Full re-index (all nodes)
    uv run python -m backend.scripts.setup_vector_index

    # Incremental (only new nodes without embeddings)
    uv run python -m backend.scripts.setup_vector_index --incremental
"""

import logging
import argparse
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_nodes_for_embedding(
    graph_service, incremental: bool = False
) -> List[Dict[str, Any]]:
    """Fetch nodes for embedding"""
    logger.info(f"Fetching nodes from Neo4j (incremental={incremental})...")

    # Base query with relationship context
    if incremental:
        # Only get nodes that don't have embeddings yet
        query = """
        MATCH (n)
        WHERE n.name IS NOT NULL AND n.embedding IS NULL
        OPTIONAL MATCH (n)-[r]-(related)
        WITH n, collect(DISTINCT {
            type: type(r),
            target_name: related.name
        })[0..10] as relationships
        RETURN 
            elementId(n) as id,
            n {.*, labels: labels(n)} as node,
            relationships
        """
    else:
        # Get all nodes
        query = """
        MATCH (n)
        WHERE n.name IS NOT NULL
        OPTIONAL MATCH (n)-[r]-(related)
        WITH n, collect(DISTINCT {
            type: type(r),
            target_name: related.name
        })[0..10] as relationships
        RETURN 
            elementId(n) as id,
            n {.*, labels: labels(n)} as node,
            relationships
        """

    results = graph_service.graph.query(query)
    logger.info(f"Found {len(results)} nodes to embed")
    return results


def create_vector_index(graph_service, index_name: str, dimension: int):
    """Create vector index in Neo4j if it doesn't exist"""
    logger.info(f"Checking vector index '{index_name}'...")

    try:
        existing = graph_service.graph.query(
            "SHOW INDEXES WHERE name = $name", {"name": index_name}
        )

        if existing:
            logger.info(f"Index '{index_name}' already exists")
            return

        # Create the index
        graph_service.graph.query(f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:EmbeddedNode)
            ON (n.embedding)
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: {dimension},
                `vector.similarity_function`: 'cosine'
            }}}}
        """)
        logger.info(f"Vector index '{index_name}' created successfully")

    except Exception as e:
        logger.error(f"Failed to create vector index: {e}")
        raise


def store_embeddings(graph_service, node_id: str, embedding: List[float]):
    """Store embedding for a single node"""
    graph_service.graph.query(
        """
        MATCH (n) WHERE elementId(n) = $node_id
        SET n.embedding = $embedding
        SET n:EmbeddedNode
        """,
        {"node_id": node_id, "embedding": embedding},
    )


def run_indexing(incremental: bool = False):
    """Main indexing function"""
    from backend.app.services.graph_service import graph_service
    from backend.app.services.embedding_service import (
        embedding_service,
        format_node_for_embedding,
        embed_texts,
    )
    from backend.app.core.config import settings

    # Connect to Neo4j
    logger.info("Connecting to Neo4j...")
    graph_service.connect()

    # Initialize embedding model
    logger.info("Initializing embedding model...")
    embedding_service.initialize()

    # Create vector index (idempotent)
    create_vector_index(
        graph_service, settings.VECTOR_INDEX_NAME, settings.VECTOR_DIMENSION
    )

    # Fetch nodes
    nodes_data = get_nodes_for_embedding(graph_service, incremental=incremental)

    if not nodes_data:
        logger.info("No new nodes to embed. Index is up to date!")
        return {"indexed": 0, "message": "Already up to date"}

    # Prepare texts for embedding
    logger.info("Formatting nodes for embedding...")
    texts = []
    node_ids = []

    for item in nodes_data:
        node = item["node"]
        relationships = item.get("relationships", [])
        text = format_node_for_embedding(node, relationships)
        texts.append(text)
        node_ids.append(item["id"])

    # Generate embeddings in batch
    logger.info(f"Generating embeddings for {len(texts)} nodes...")
    embeddings = embed_texts(texts)

    # Store embeddings
    logger.info("Storing embeddings in Neo4j...")
    for i, (node_id, embedding) in enumerate(zip(node_ids, embeddings)):
        store_embeddings(graph_service, node_id, embedding)
        if (i + 1) % 100 == 0:
            logger.info(f"Stored {i + 1}/{len(node_ids)} embeddings")

    logger.info(f"✅ Successfully indexed {len(embeddings)} nodes with embeddings!")
    return {"indexed": len(embeddings), "message": "Indexing complete"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Setup vector index for semantic search"
    )
    parser.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Only embed nodes without existing embeddings",
    )
    args = parser.parse_args()

    run_indexing(incremental=args.incremental)
