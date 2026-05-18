"""Text chunker — split long documents into overlapping chunks."""
from __future__ import annotations

import re
import logging

logger = logging.getLogger(__name__)

# Sentence boundary pattern: period, question mark, exclamation followed by space/end
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Split text into overlapping character-based chunks.

    Tries to break at sentence boundaries near the target chunk size.
    Falls back to character-based splitting at a word boundary if no sentence
    break is found.

    Args:
        text: The input text to chunk.
        chunk_size: Target size of each chunk in characters (default 512).
        overlap: Number of overlapping characters between consecutive chunks (default 64).

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    text_len = len(text)

    if text_len <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            chunks.append(text[start:].strip())
            break

        # Look back from the target end to find a good sentence break point
        search_region = text[max(start, end - min(chunk_size // 2, 200)):end]
        sentence_breaks = list(_SENTENCE_BOUNDARY.finditer(search_region))

        if sentence_breaks:
            # Use the last sentence break in the search region
            last_break = sentence_breaks[-1]
            actual_end = end - len(search_region) + last_break.start() + 1  # include the sentence-terminating char
        else:
            # Fallback: break at a space near the target size
            # Search backwards from end for the nearest space
            space_idx = text.rfind(" ", start, end)
            if space_idx > start + chunk_size // 4:
                actual_end = space_idx
            else:
                # Hard break at chunk_size if no good word boundary
                actual_end = end

        chunk = text[start:actual_end].strip()
        if chunk:
            chunks.append(chunk)

        # Next chunk starts with overlap, but advances at least one character
        next_start = actual_end - overlap
        if next_start <= start:
            next_start = start + len(chunk)
        start = next_start

    logger.info("Chunked %d-character text into %d chunks (size=%d, overlap=%d)",
                text_len, len(chunks), chunk_size, overlap)
    return chunks
