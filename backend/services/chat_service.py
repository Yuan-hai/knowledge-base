"""Chat service — SSE streaming chat via DashScope API (OpenAI-compatible)."""
from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

import httpx
from config import DASHSCOPE_API_KEY, DASHSCOPE_CHAT_URL

logger = logging.getLogger(__name__)


async def stream_chat(messages: list[dict], model: str = "qwen-plus") -> AsyncGenerator[str, None]:
    """Call Dashscope chat API and yield SSE text chunks.

    Uses the OpenAI-compatible chat completions endpoint with stream=True
    and parses Server-Sent Events from the response.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        model: Model identifier (e.g. 'qwen-plus', 'qwen-turbo', 'qwen-max').

    Yields:
        Text content chunks extracted from the streaming response.
        On error, yields an error message string.
    """
    if not DASHSCOPE_API_KEY:
        yield f"data: {json.dumps({'error': 'DASHSCOPE_API_KEY is not configured'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    logger.info("Starting chat stream: model=%s, message_count=%d", model, len(messages))

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST", DASHSCOPE_CHAT_URL, json=payload, headers=headers
            ) as response:
                if response.status_code != 200:
                    error_body = ""
                    async for chunk in response.aiter_text():
                        error_body += chunk
                    logger.error("Chat API error [%d]: %s", response.status_code, error_body[:500])
                    yield f"data: {json.dumps({'error': f'Chat API returned HTTP {response.status_code}'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]

                    if data_str.strip() == "[DONE]":
                        logger.debug("Chat stream received [DONE] signal")
                        yield "data: [DONE]\n\n"
                        return

                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            sse_chunk = json.dumps({"choices": [{"delta": {"content": content}}]})
                            yield f"data: {sse_chunk}\n\n"
                    except (json.JSONDecodeError, IndexError, KeyError) as e:
                        logger.debug("Skipping unparseable SSE line (%s): %s...", e, data_str[:80])
                        continue

    except httpx.HTTPError as e:
        logger.error("HTTP transport error during chat stream: %s", e)
        yield f"data: {json.dumps({'error': f'Connection to chat API failed — {e}'})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception:
        logger.exception("Unexpected error during chat stream")
        yield "data: {}\n\n".format(json.dumps({"error": "An unexpected error occurred during chat streaming."}))
        yield "data: [DONE]\n\n"
