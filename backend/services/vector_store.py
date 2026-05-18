"""Vector store — numpy-backed JSON storage with cosine similarity search."""
from __future__ import annotations

import json
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
STORE_FILE = DATA_DIR / "vectors.json"

_store: list[dict] = []


def _load() -> list[dict]:
    global _store
    if _store:
        return _store
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STORE_FILE.exists():
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            _store = json.load(f)
    return _store


def _save() -> None:
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(_store, f, ensure_ascii=False)


def _cosine_sim(a: list[float], b: list[float]) -> float:
    a_np = np.array(a)
    b_np = np.array(b)
    dot = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def add_documents(
    doc_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    metadata: dict,
) -> None:
    if not chunks:
        logger.warning("add_documents called with empty chunks for doc_id=%s", doc_id)
        return

    data = _load()
    for i, chunk in enumerate(chunks):
        entry = {
            "chunk_id": f"{doc_id}_chunk_{i}",
            "doc_id": doc_id,
            "chunk_index": i,
            "document": chunk,
            "embedding": embeddings[i],
            "filename": metadata.get("filename", "unknown"),
        }
        data.append(entry)
    _save()
    _store = data
    logger.info("Added %d chunks for document '%s'", len(chunks), doc_id)


def search(
    query_embedding: list[float],
    doc_ids: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    data = _load()
    if not data:
        return []

    scored: list[tuple[float, dict]] = []
    for entry in data:
        if doc_ids and entry["doc_id"] not in doc_ids:
            continue
        sim = _cosine_sim(query_embedding, entry["embedding"])
        scored.append((sim, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results = []
    for score, entry in top:
        results.append({
            "id": entry["chunk_id"],
            "document": entry["document"],
            "metadata": {
                "doc_id": entry["doc_id"],
                "filename": entry["filename"],
                "chunk_index": entry["chunk_index"],
            },
            "distance": 1.0 - score,
        })
    logger.info("Vector search returned %d results (top_k=%d)", len(results), top_k)
    return results


def delete_document(doc_id: str) -> None:
    data = _load()
    before = len(data)
    data = [e for e in data if e["doc_id"] != doc_id]
    _store = data
    _save()
    logger.info("Deleted %d chunks for document '%s'", before - len(data), doc_id)


def get_unique_documents() -> list[dict]:
    data = _load()
    doc_map: dict[str, dict] = {}
    for entry in data:
        d_id = entry["doc_id"]
        if d_id not in doc_map:
            doc_map[d_id] = {
                "doc_id": d_id,
                "filename": entry.get("filename", "unknown"),
                "chunk_count": 0,
            }
        doc_map[d_id]["chunk_count"] += 1
    return list(doc_map.values())
