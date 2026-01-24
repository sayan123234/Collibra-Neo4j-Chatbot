from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.app.services.chat_service import chat_service
from backend.app.services.graph_service import graph_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    answer: str
    cypher_query: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a natural language question and return the answer + metadata.
    """
    result = await chat_service.process_question(request.message, request.history)

    if "error" in result:
        # We could raise HTTPException here, but often chatbots prefer to return the error in the body
        # so the UI can display it gracefully.
        return ChatResponse(
            answer="I encountered an error processing your request.",
            error=result["error"],
        )

    return ChatResponse(
        answer=result["answer"],
        cypher_query=result.get("cypher_query"),
        results=result.get("results"),
    )


@router.get("/schema")
def get_schema():
    """Get the current graph schema"""
    try:
        return {"schema": graph_service.get_schema()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
