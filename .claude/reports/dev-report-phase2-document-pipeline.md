# Phase 2: Document Processing Pipeline — Completion Report

**Date:** 2026-05-18

## Summary

Implemented the full backend document processing pipeline: file parsing, text chunking, embedding generation via DashScope API, and persistent storage in ChromaDB. Three REST endpoints for upload, list, and delete are now fully functional.

## Files Created

### Utilities (`backend/utils/`)

| File | Purpose |
|------|---------|
| `backend/utils/document_parser.py` | PDF parsing (PyPDF2) and DOCX parsing (python-docx) with auto-detection by file extension. Raises `ValueError` for unsupported formats or empty documents. |
| `backend/utils/text_chunker.py` | Character-based text splitting with configurable chunk size (default 512) and overlap (default 64). Tries to break at sentence boundaries, falls back to word boundaries, then hard break. |

### Services (`backend/services/`)

| File | Purpose |
|------|---------|
| `backend/services/embedding_service.py` | Async embeddings via DashScope `text-embedding-v3` (1024-dim). Uses `httpx.AsyncClient`, handles auth via `DASHSCOPE_API_KEY`, raises `RuntimeError` on API failure. |
| `backend/services/vector_store.py` | ChromaDB `PersistentClient` at `backend/data/chromadb/`. Functions: `add_documents`, `search` (with optional doc_id filter), `delete_document`, `get_unique_documents`, `clear_collection`. Uses cosine distance metric. |
| `backend/services/document_service.py` | Orchestration layer: `process_upload` (parse -> chunk -> embed -> store), `list_documents`, `delete_document`. Generates UUID4 document IDs and ISO timestamps. |

### Routers (modified)

| File | Action |
|------|--------|
| `backend/routers/documents.py` | **Rewritten** from 501 stubs to full implementation with `POST /api/documents/upload` (multipart file), `GET /api/documents/` (list), `DELETE /api/documents/{id}` (delete). |

## Key Design Decisions

- **Document IDs**: UUID4 strings, unique per upload even if the same filename is re-uploaded.
- **Embedding batching**: All chunks for a document are sent in a single DashScope API call (the API accepts a list of texts).
- **Error classification**: `ValueError` for client errors (bad format, empty doc) -> HTTP 400. `RuntimeError` for server/infra errors (API failure, DB failure) -> HTTP 500.
- **File collision**: If a file with the same name already exists in the upload folder, a random 8-char suffix is appended to avoid overwrites.
- **ChromaDB metric**: Cosine similarity (`hnsw:space: cosine`) for semantic search.
- **ChromaDB data**: Stored under `backend/data/chromadb/`.

## Files NOT Modified

- `backend/config.py` — unchanged
- `backend/models/schemas.py` — unchanged
- `backend/routers/settings.py` — unchanged
- `backend/main.py` — unchanged
