from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ReindexRequest(BaseModel):
    incremental: bool = True  # Default to incremental for safety


class ReindexResponse(BaseModel):
    status: str
    message: str
    indexed: Optional[int] = None


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_embeddings(
    request: ReindexRequest, background_tasks: BackgroundTasks
):
    """
    Trigger re-indexing of node embeddings for semantic search.

    - incremental=True: Only embed nodes without existing embeddings (default)
    - incremental=False: Re-embed all nodes (slower)
    """
    try:
        # Import here to avoid circular imports and lazy load heavy dependencies
        from backend.scripts.setup_vector_index import run_indexing

        # Run indexing in background to not block the request
        background_tasks.add_task(run_indexing, request.incremental)

        return ReindexResponse(
            status="started",
            message=f"Re-indexing started in background (incremental={request.incremental})",
        )

    except Exception as e:
        logger.error(f"Failed to start reindexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index-status")
async def get_index_status():
    """
    Check the status of the vector index and embedding coverage.
    """
    try:
        from backend.app.services.graph_service import graph_service
        from backend.app.core.config import settings

        if not graph_service.graph:
            graph_service.connect()

        # Check if index exists
        index_exists = graph_service.check_vector_index_exists()

        # Count nodes with and without embeddings
        stats = graph_service.graph.query("""
            MATCH (n) WHERE n.name IS NOT NULL
            RETURN 
                count(n) as total_nodes,
                count(n.embedding) as embedded_nodes
        """)

        total = stats[0]["total_nodes"] if stats else 0
        embedded = stats[0]["embedded_nodes"] if stats else 0

        return {
            "index_name": settings.VECTOR_INDEX_NAME,
            "index_exists": index_exists,
            "total_nodes": total,
            "embedded_nodes": embedded,
            "pending_nodes": total - embedded,
            "coverage_percent": round((embedded / total * 100) if total > 0 else 0, 2),
        }

    except Exception as e:
        logger.error(f"Failed to get index status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
