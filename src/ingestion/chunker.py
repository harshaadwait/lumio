"""
chunker.py — Splits raw page text into overlapping chunks for vector embedding.
Uses paragraph-aware splitting to preserve semantic coherence.
"""

import os
import re
from typing import List, Dict, Any

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to split on paragraph boundaries first, then sentence boundaries.
    """
    # Clean whitespace
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r" {2,}", " ", text)

    # Split on paragraph breaks
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Overlap: carry last `overlap` chars into next chunk
                overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
                current_chunk = overlap_text + "\n\n" + para
            else:
                # Single paragraph exceeds chunk_size — split by sentence
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= chunk_size:
                        current_chunk += (" " if current_chunk else "") + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return [c for c in chunks if len(c) > 50]  # Filter trivially short chunks


def chunk_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes list of page dicts and returns list of chunk dicts with full metadata.
    Each chunk gets a unique chunk_id.
    """
    chunks = []

    for page in pages:
        page_chunks = split_into_chunks(page["text"])

        for i, chunk_text in enumerate(page_chunks):
            chunk_id = f"{page['problem_tag']}__p{page['page_num']}__c{i}"
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "problem_tag": page["problem_tag"],
                "page_num": page["page_num"],
                "source_file": page["source_file"],
            })

    return chunks
