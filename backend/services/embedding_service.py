"""Embedding service — generate text embeddings via DashScope API."""
from __future__ import annotations

import logging
import httpx
from config import DASHSCOPE_API_KEY, DASHSCOPE_EMBEDDING_URL, DASHSCOPE_EMBEDDING_MODEL

logger = logging.getLogger(__name__)


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using DashScope text-embedding-v3.

    Args:
        texts: List of input text strings to embed.

    Returns:
        List of embedding vectors, each a 1024-dimensional list of floats.

    Raises:
        ValueError: If the API key is not configured.
        RuntimeError: If the API request fails.
    """
    if not DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY is not configured. Set it in settings or environment.")

    if not texts:
        return []

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": DASHSCOPE_EMBEDDING_MODEL,
        "input": {"texts": texts},
        "parameters": {"text_type": "document"},
    }

    logger.info("Requesting embeddings for %d texts (model=%s)", len(texts), DASHSCOPE_EMBEDDING_MODEL)

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(DASHSCOPE_EMBEDDING_URL, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error("DashScope embedding API error [%d]: %s", response.status_code, response.text)
            raise RuntimeError(f"Embedding API returned {response.status_code}: {response.text}")

        data = response.json()
        embeddings: list[list[float]] = []
        for emb in data.get("output", {}).get("embeddings", []):
            embeddings.append(emb.get("embedding", []))

        if not embeddings:
            raise RuntimeError(f"Embedding API returned no embeddings. Response: {data}")

        logger.info("Received %d embeddings (%d-dim)", len(embeddings), len(embeddings[0]) if embeddings else 0)
        return embeddings
