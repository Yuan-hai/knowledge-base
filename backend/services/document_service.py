"""Document service — orchestrate parsing, chunking, embedding, and storage."""
from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

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
        "file_path": file_path,
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
            "created_at": d.get("created_at", ""),
            "chunk_count": d["chunk_count"],
            "file_path": d.get("file_path", ""),
        }
        for d in docs
    ]


def delete_document(doc_id: str, upload_folder: str = "") -> None:
    """Delete a document, its physical file, and all its chunks.

    Retrieves the filename and file_path from the vector store, deletes the
    physical file from disk (if found), then removes the vector store entries.

    Args:
        doc_id: The document identifier to remove.
        upload_folder: Path to the upload directory for filename-based lookup.
    """
    # Retrieve document info (filename, file_path) before deleting from vector store
    docs = get_unique_documents()
    filename = None
    file_path = None
    for d in docs:
        if d.get("doc_id") == doc_id:
            filename = d.get("filename")
            file_path = d.get("file_path")
            break

    # Try to delete the physical file
    deleted_physical = False
    # 1) Use the stored file_path if available and the file exists
    if file_path:
        fp = Path(file_path)
        if fp.exists():
            fp.unlink()
            deleted_physical = True
            logger.info("Deleted physical file via stored path: %s", file_path)

    # 2) Fallback: search upload_folder by filename
    if not deleted_physical and filename and upload_folder:
        candidate = Path(upload_folder) / filename
        if candidate.exists():
            candidate.unlink()
            deleted_physical = True
            logger.info("Deleted physical file via upload folder: %s", candidate)

    if not deleted_physical and filename:
        logger.warning("Could not find physical file for document '%s' (filename=%s, file_path=%s)",
                       doc_id, filename, file_path)

    # Delete from vector store
    vs_delete(doc_id)
    logger.info("Document '%s' deleted from vector store", doc_id)
