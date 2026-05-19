"""Embedding service — generate text embeddings via DashScope or OpenAI-compatible API."""
from __future__ import annotations

import logging
import httpx
from config import DASHSCOPE_API_KEY, DASHSCOPE_EMBEDDING_URL, DASHSCOPE_EMBEDDING_MODEL, load_settings

logger = logging.getLogger(__name__)


def _is_dashscope(url: str) -> bool:
    """Detect whether the given URL targets a DashScope-compatible embedding endpoint."""
    return "dashscope" in url.lower()


def _build_payload(embedding_model: str, texts: list[str], is_dashscope: bool) -> dict:
    """Build the request payload for the embedding API."""
    if is_dashscope:
        return {
            "model": embedding_model,
            "input": {"texts": texts},
            "parameters": {"text_type": "document"},
        }
    else:
        return {
            "model": embedding_model,
            "input": texts,
        }


def _parse_dashscope_response(data: dict) -> list[list[float]]:
    """Parse a DashScope-format embedding response."""
    embeddings: list[list[float]] = []
    for emb in data.get("output", {}).get("embeddings", []):
        embeddings.append(emb.get("embedding", []))
    return embeddings


def _parse_openai_response(data: dict) -> list[list[float]]:
    """Parse an OpenAI-compatible embedding response."""
    items = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
    return [item["embedding"] for item in items]


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using the configured embedding API.

    Automatically detects the API format from the URL:
    - URLs containing "dashscope" use the DashScope payload/response format.
    - All other URLs use the OpenAI-compatible format (DeepSeek, Ollama, etc.).

    Args:
        texts: List of input text strings to embed.

    Returns:
        List of embedding vectors, each a 1024-dimensional list of floats.

    Raises:
        ValueError: If the API key is not configured.
        RuntimeError: If the API request fails.
    """
    # Load settings for api_key, embedding URL, and embedding model; fallback to env/hardcoded defaults
    settings = load_settings()
    api_key = (settings.get("api_key") or "").strip() or DASHSCOPE_API_KEY
    embedding_url = (settings.get("api_embedding_url") or "").strip() or DASHSCOPE_EMBEDDING_URL
    embedding_model = (settings.get("embedding_model") or "").strip() or DASHSCOPE_EMBEDDING_MODEL

    if not api_key:
        raise ValueError("API key is not configured. Set it in settings or the DASHSCOPE_API_KEY environment variable.")

    if not texts:
        return []

    dashscope = _is_dashscope(embedding_url)
    payload = _build_payload(embedding_model, texts, dashscope)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    logger.info("Requesting embeddings for %d texts (model=%s, format=%s)",
                len(texts), embedding_model, "dashscope" if dashscope else "openai")

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(embedding_url, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error("Embedding API error [%d]: %s", response.status_code, response.text[:500])
            raise RuntimeError(f"Embedding API returned {response.status_code}: {response.text[:500]}")

        data = response.json()

        if dashscope:
            embeddings = _parse_dashscope_response(data)
        else:
            embeddings = _parse_openai_response(data)

        if not embeddings:
            raise RuntimeError(f"Embedding API returned no embeddings. Response: {data}")

        logger.info("Received %d embeddings (%d-dim)", len(embeddings), len(embeddings[0]) if embeddings else 0)
        return embeddings
