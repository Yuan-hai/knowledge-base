"""AI chat endpoint — SSE streaming via DashScope."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
from services.chat_service import stream_chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(body: ChatRequest):
    """Stream AI chat response via SSE.

    Accepts a list of messages and an optional model selection,
    then streams the LLM response back as text/event-stream.
    """
    return StreamingResponse(
        stream_chat([m.model_dump() for m in body.messages], body.model),
        media_type="text/event-stream",
    )
