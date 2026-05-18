"""RAG service — retrieval-augmented generation with SSE streaming."""
from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from services.embedding_service import get_embeddings
from services.vector_store import search
from services.chat_service import stream_chat

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = (
    "You are a helpful research assistant. Use the following retrieved document context "
    "to answer the user's question.\n\n"
    "Guidelines:\n"
    "- Answer based on the provided context. If the context does not contain relevant "
    "information, say so honestly.\n"
    "- Cite sources inline using the source index like [1], [2], etc.\n"
    "- Be concise and accurate.\n"
    "- Do not mention \"the context\" or \"the provided text\" in your answer — speak "
    "naturally as if you know the information."
)


def _build_context(chunks: list[dict]) -> str:
    """Build a formatted context string from retrieved chunks.

    Each chunk is prefixed with a source index that the LLM can cite as [1], [2], etc.
    """
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        filename = chunk.get("metadata", {}).get("filename", "Unknown")
        text = chunk.get("document", "")
        parts.append(f"[{i}] Source: {filename}\n{text}")
    return "\n\n".join(parts)


async def _yield_sources(sources: list[dict]) -> str:
    """Build a JSON sources block appended after the answer.

    The frontend can detect and parse this marker to render a sources panel.
    Format: <!--SOURCES:<json>-->
    """
    formatted: list[dict] = []
    for src in sources:
        excerpt = (src.get("document", "") or "")[:200]
        formatted.append({
            "id": src.get("id", ""),
            "filename": src.get("metadata", {}).get("filename", "Unknown"),
            "excerpt": excerpt,
            "distance": round(src.get("distance", 0.0), 4),
        })
    return json.dumps({"type": "sources", "data": formatted}, ensure_ascii=False)


async def stream_rag_query(
    query: str,
    document_ids: list[str],
    model: str = "qwen-plus",
    top_k: int = 5,
) -> AsyncGenerator[str, None]:
    """Stream a RAG query response with source citations.

    Pipeline:
        1. Embed the user query into a vector.
        2. Search the vector store for relevant document chunks.
        3. Build a context-augmented prompt with sources.
        4. Stream the LLM response via the chat service.
        5. Append a structured sources block that the frontend can render.

    Args:
        query: The user's question.
        document_ids: Restrict search to these document IDs.
        model: LLM model to use for generation.
        top_k: Number of top chunks to retrieve from the vector store.

    Yields:
        Text chunks from the LLM, then a sources marker.
    """
    # 1. Embed the user query
    try:
        embeddings = await get_embeddings([query])
        query_embedding = embeddings[0]
    except Exception as e:
        logger.error("Failed to embed query: %s", e)
        yield f"data: {json.dumps({'error': f'Failed to generate query embedding — {e}'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # 2. Search the vector store
    try:
        results = search(
            query_embedding,
            doc_ids=document_ids if document_ids else None,
            top_k=top_k,
        )
    except Exception as e:
        logger.error("Failed to search vector store: %s", e)
        yield f"data: {json.dumps({'error': f'Failed to search knowledge base — {e}'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    if not results:
        yield "data: " + json.dumps({"choices": [{"delta": {"content": (
            "No relevant documents found for your query. "
            "Please upload some documents first or broaden your search scope."
        )}}]}) + "\n\n"
        yield "data: [DONE]\n\n"
        return

    # 3. Build context and construct the prompt
    context = _build_context(results)

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n\n{context}\n\nQuestion: {query}"},
    ]

    logger.info(
        "RAG query: top_k=%d, retrieved_chunks=%d, model=%s, doc_ids=%s",
        top_k,
        len(results),
        model,
        document_ids,
    )

    # 4. Stream chat response (already SSE-formatted)
    async for chunk in stream_chat(messages, model=model):
        yield chunk

    # 5. Append sources marker as SSE content chunk
    try:
        sources_json = await _yield_sources(results)
        content = f"\n\n<!--SOURCES:{sources_json}-->"
        sse = json.dumps({"choices": [{"delta": {"content": content}}]})
        yield f"data: {sse}\n\n"
        yield "data: [DONE]\n\n"
    except Exception:
        logger.exception("Failed to build sources marker")
        yield "data: [DONE]\n\n"
