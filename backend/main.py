"""Library knowledge base — FastAPI application entry point."""

import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import load_settings
from routers import documents, chat, rag, settings
from services.document_service import list_documents as list_docs, process_upload

logger = logging.getLogger(__name__)

app = FastAPI(title="Library", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@app.on_event("startup")
async def startup():
    """Schedule the document scan as a background task so the server is ready immediately."""
    asyncio.create_task(scan_and_index_existing_files())


async def scan_and_index_existing_files():
    """Scan the upload folder for PDF/DOCX files.

    Files that are already indexed in the vector store (matched by filename)
    are skipped. New files are automatically processed through the full pipeline.
    """
    settings = load_settings()
    upload_folder = settings.get("upload_folder", "")
    if not upload_folder:
        logger.info("No upload_folder configured, skipping startup scan.")
        return

    upload_dir = Path(upload_folder)
    if not upload_dir.exists():
        logger.info("Upload folder '%s' does not exist, skipping startup scan.", upload_folder)
        return

    # Deduplicate first
    from services.vector_store import deduplicate_documents
    deduplicate_documents()

    # Collect existing file_paths from the vector store
    try:
        existing_docs = list_docs()
    except Exception as e:
        logger.warning("Could not list existing documents during startup scan: %s", e)
        existing_docs = []

    existing_file_paths = {d.get("file_path", "") for d in existing_docs if d.get("file_path")}

    # Scan upload folder
    for file_path in upload_dir.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        filename = file_path.name
        if str(file_path.resolve()) in existing_file_paths:
            logger.debug("Skipping already-indexed file: %s", filename)
            continue

        logger.info("Startup scan: processing new file '%s'", filename)
        try:
            result = await process_upload(str(file_path), filename)
            logger.info("Startup scan: indexed '%s' (%d chunks)", filename, result.get("chunk_count", 0))
        except Exception as e:
            logger.error("Startup scan: failed to process '%s': %s", filename, e)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
