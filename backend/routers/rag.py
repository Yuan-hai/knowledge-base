"""RAG query endpoint — retrieval-augmented generation with SSE."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import RagQueryRequest
from services.rag_service import stream_rag_query

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query")
async def rag_query(body: RagQueryRequest):
    """Stream RAG query response with source citations.

    Embeds the user query, retrieves the top-k most relevant chunks
    from the vector store, augments the prompt with that context,
    and streams the LLM answer with inline source citations.
    """
    return StreamingResponse(
        stream_rag_query(body.query, body.document_ids, body.model, body.top_k),
        media_type="text/event-stream",
    )
