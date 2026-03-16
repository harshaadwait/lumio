"""
metadata_tagger.py — Enriches raw chunks with full book metadata from the registry.
This is the key layer that enables problem-filtered retrieval in ChromaDB.
"""

from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.book_registry import BOOK_BY_TAG


def tag_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merges chunk data with full book registry metadata.
    Chunks missing from registry get tagged as 'unknown'.
    """
    tagged = []

    for chunk in chunks:
        tag = chunk.get("problem_tag", "unknown")
        book_meta = BOOK_BY_TAG.get(tag, {
            "problem_tag": tag,
            "problem_label": "Unknown",
            "book_title": "Unknown",
            "author": "Unknown",
            "core_insight": "",
            "action_prompt": "",
        })

        tagged_chunk = {
            # Core content
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            # ChromaDB metadata (all must be str/int/float/bool — no lists/dicts)
            "problem_tag": book_meta["problem_tag"],
            "problem_label": book_meta["problem_label"],
            "book_title": book_meta["book_title"],
            "author": book_meta["author"],
            "core_insight": book_meta["core_insight"],
            "action_prompt": book_meta["action_prompt"],
            "page_num": chunk["page_num"],
            "source_file": chunk["source_file"],
        }
        tagged.append(tagged_chunk)

    return tagged
