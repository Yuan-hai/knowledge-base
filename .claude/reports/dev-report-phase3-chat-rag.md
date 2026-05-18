# Phase 3 — Chat & RAG Services with SSE Streaming

## Status: Complete

## Files Created

### 1. `backend/services/chat_service.py` (NEW)
Chat service that calls the DashScope OpenAI-compatible chat API with streaming.
- **`stream_chat(messages, model)`** — Async generator that POSTs to `DASHSCOPE_CHAT_URL` with `stream: true`, parses SSE `data:` lines, extracts `choices[0].delta.content`, and yields text chunks.
- Handles `[DONE]` end-of-stream signal.
- Validates `DASHSCOPE_API_KEY` is configured before making requests.
- Graceful error handling: HTTP errors are caught and yield descriptive error messages; JSON parse failures on malformed SSE lines are logged and skipped.
- Uses `httpx.AsyncClient` with a 120-second timeout and `client.stream()` for streaming responses.

### 2. `backend/services/rag_service.py` (NEW)
Retrieval-Augmented Generation service with a 5-step pipeline:
1. **Embed** the user query via `get_embeddings()`.
2. **Search** the vector store via `search()` with optional `doc_ids` filter.
3. **Build context** from retrieved chunks, formatted with source indices `[1]`, `[2]`, etc., prefixed by filename.
4. **Stream** the LLM response via `stream_chat()` with a system prompt instructing inline source citations.
5. **Append** a structured `<!--SOURCES:{json}-->` marker after the answer so the frontend can render a sources panel.

Key functions:
- **`_build_context(chunks)`** — Formats chunks as numbered source blocks with filenames.
- **`_yield_sources(sources)`** — Serializes source metadata (id, filename, excerpt, distance) into JSON.
- **`stream_rag_query(query, document_ids, model, top_k)`** — Main entry point; orchestrates the full pipeline.

### 3. `backend/routers/chat.py` (REWRITTEN)
Replaced the `501 Not Implemented` stub with a working SSE streaming endpoint.
- Accepts `POST /api/chat` with a `ChatRequest` body.
- Returns `StreamingResponse` with `media_type="text/event-stream"`.
- Converts Pydantic `ChatMessage` models to dicts via `model_dump()` before passing to the service.

### 4. `backend/routers/rag.py` (REWRITTEN)
Replaced the `501 Not Implemented` stub with a working RAG streaming endpoint.
- Accepts `POST /api/rag/query` with a `RagQueryRequest` body.
- Returns `StreamingResponse` with `media_type="text/event-stream"`.
- Passes all request parameters (`query`, `document_ids`, `model`, `top_k`) through to `stream_rag_query()`.

## Files Not Modified
- `backend/main.py` — Router mounts unchanged.
- `backend/config.py` — Settings unchanged.
- `backend/models/schemas.py` — Pydantic models unchanged.
- `backend/services/embedding_service.py` — Embedding service unchanged.
- `backend/services/vector_store.py` — Vector store unchanged.

## Architecture

```
POST /api/chat
  → routers/chat.py
    → services/chat_service.py → DashScope Chat API (SSE)
      → yield text chunks to client

POST /api/rag/query
  → routers/rag.py
    → services/rag_service.py
      → services/embedding_service.py → DashScope Embedding API
      → services/vector_store.py → ChromaDB similarity search
      → services/chat_service.py → DashScope Chat API (SSE)
        → yield answer + sources marker to client
```

## Key Design Decisions
- **SSE via `text/event-stream`**: DashScope's OpenAI-compatible endpoint returns standard SSE. The `StreamingResponse` passes chunks through directly to the frontend.
- **Inline citations + structured marker**: The LLM is prompted to cite sources inline as `[1]`, `[2]`, etc. A JSON marker `<!--SOURCES:...-->` is appended after the answer for the frontend to render a formal sources panel.
- **Error resilience**: Each stage of the RAG pipeline (embedding, search, generation) has its own try/except, yielding user-facing error messages rather than crashing the stream.
- **No modifications to existing files**: The implementation is purely additive, with zero changes to `main.py`, `config.py`, `schemas.py`, or Phase 2 services.
