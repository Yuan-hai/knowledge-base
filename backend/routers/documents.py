"""Document upload, list, delete endpoints — full implementation."""
from __future__ import annotations

import shutil
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from config import load_settings
from models.schemas import DocumentInfo
from services.document_service import process_upload, list_documents, delete_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _get_upload_dir() -> Path:
    """Get the configured upload directory, creating it if needed."""
    settings = load_settings()
    upload_folder = settings.get("upload_folder", "G:/documents/knowledge-base")
    upload_dir = Path(upload_folder)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF or DOCX).

    The file is saved to the configured upload folder, then processed through
    the pipeline: parse -> chunk -> embed -> store in ChromaDB.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    upload_dir = _get_upload_dir()
    safe_filename = Path(file.filename).name
    dest_path = upload_dir / safe_filename

    # Avoid overwriting: append a suffix if file exists
    if dest_path.exists():
        stem = dest_path.stem
        suffix = dest_path.suffix
        import uuid
        dest_path = upload_dir / f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"

    try:
        # Save uploaded file to disk
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("Saved uploaded file to %s", dest_path)

        # Check if this file_path is already indexed (dedup)
        existing = list_documents()
        existing_paths = {d.get("file_path", "") for d in existing}
        if str(dest_path.resolve()) in existing_paths:
            # Already indexed, return existing record
            for d in existing:
                if d.get("file_path") == str(dest_path.resolve()):
                    return DocumentInfo(**d)

        # Process through pipeline
        result = await process_upload(str(dest_path), file.filename)
        return DocumentInfo(**result)

    except ValueError as e:
        logger.warning("Validation error for '%s': %s", file.filename, e)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error("Processing error for '%s': %s", file.filename, e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error processing '%s'", file.filename)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@router.get("", response_model=List[DocumentInfo])
async def get_documents():
    """List all uploaded documents with their chunk counts."""
    try:
        docs = list_documents()
        return [DocumentInfo(**d) for d in docs]
    except Exception as e:
        logger.exception("Failed to list documents")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {e}")


@router.delete("/{document_id}")
async def remove_document(document_id: str):
    """Delete a document, its physical file, and all its chunks."""
    try:
        upload_dir = _get_upload_dir()
        delete_document(document_id, str(upload_dir))
        return {"status": "deleted", "document_id": document_id}
    except Exception as e:
        logger.exception("Failed to delete document '%s'", document_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {e}")
