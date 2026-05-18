"""Document service — orchestrate parsing, chunking, embedding, and storage."""
from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone

from utils.document_parser import parse_document
from utils.text_chunker import chunk_text
from services.embedding_service import get_embeddings
from services.vector_store import add_documents, delete_document as vs_delete, get_unique_documents

logger = logging.getLogger(__name__)


async def process_upload(file_path: str, filename: str) -> dict:
    """Process an uploaded document through the full pipeline.

    Steps: parse -> chunk -> embed -> store in ChromaDB.

    Args:
        file_path: Path to the uploaded document file.
        filename: Original filename (for metadata).

    Returns:
        DocumentInfo-compatible dict with id, filename, created_at, chunk_count.

    Raises:
        ValueError: If parsing fails (unsupported format, empty document).
        RuntimeError: If embedding or storage fails.
    """
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Parse
    logger.info("Processing upload: %s (id=%s)", filename, doc_id)
    try:
        text = parse_document(file_path)
    except ValueError:
        raise
    except Exception as e:
        logger.error("Document parsing failed for %s: %s", filename, e)
        raise ValueError(f"Failed to parse document '{filename}': {e}")

    # Step 2: Chunk
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError(f"Document '{filename}' produced no chunks after parsing")
    logger.info("Document '%s' split into %d chunks", filename, len(chunks))

    # Step 3: Embed
    try:
        embeddings = await get_embeddings(chunks)
    except Exception as e:
        logger.error("Embedding generation failed for %s: %s", filename, e)
        raise RuntimeError(f"Failed to generate embeddings for '{filename}': {e}")

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"Embedding count mismatch: got {len(embeddings)} embeddings for {len(chunks)} chunks"
        )

    # Step 4: Store
    metadata = {
        "filename": filename,
        "doc_id": doc_id,
        "created_at": now,
    }
    try:
        add_documents(doc_id, chunks, embeddings, metadata)
    except Exception as e:
        logger.error("Vector store insertion failed for %s: %s", filename, e)
        raise RuntimeError(f"Failed to store document '{filename}' in vector database: {e}")

    logger.info("Document '%s' processed successfully: %d chunks stored", filename, len(chunks))
    return {
        "id": doc_id,
        "filename": filename,
        "created_at": now,
        "chunk_count": len(chunks),
    }


def list_documents() -> list[dict]:
    """List all unique documents stored in the vector database.

    Returns:
        List of dicts with keys: doc_id, filename, chunk_count.
    """
    docs = get_unique_documents()
    return [
        {
            "id": d["doc_id"],
            "filename": d["filename"],
            "chunk_count": d["chunk_count"],
        }
        for d in docs
    ]


def delete_document(doc_id: str) -> None:
    """Delete a document and all its chunks from the vector store.

    Args:
        doc_id: The document identifier to remove.
    """
    vs_delete(doc_id)
    logger.info("Document '%s' deleted", doc_id)
