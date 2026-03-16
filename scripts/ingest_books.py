"""
ingest_books.py — Full ingestion pipeline runner.

Steps:
  1. Load PDFs from data/books/
  2. Chunk text with overlap
  3. Tag chunks with book metadata
  4. Embed + upsert into ChromaDB

Run: python scripts/ingest_books.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.ingestion.pdf_loader import load_all_books
from src.ingestion.chunker import chunk_pages
from src.ingestion.metadata_tagger import tag_chunks
from src.vectorstore.chroma_store import upsert_chunks, collection_stats


def main():
    print("=" * 60)
    print("  Lumio — Book Ingestion Pipeline")
    print("  Illuminate your blind spots with AI")
    print("=" * 60)

    # Step 1: Load PDFs
    print("\n[1/4] Loading PDFs from data/books/...")
    pages = load_all_books()
    print(f"  ✓ {len(pages)} pages loaded from PDFs")

    # Step 2: Chunk
    print("\n[2/4] Chunking text...")
    chunks = chunk_pages(pages)
    print(f"  ✓ {len(chunks)} chunks created")

    # Step 3: Tag with metadata
    print("\n[3/4] Tagging chunks with book metadata...")
    tagged_chunks = tag_chunks(chunks)
    
    # Show breakdown by book
    from collections import Counter
    tag_counts = Counter(c["problem_tag"] for c in tagged_chunks)
    for tag, count in sorted(tag_counts.items()):
        print(f"    {tag}: {count} chunks")

    # Step 4: Embed + upsert
    print(f"\n[4/4] Embedding and upserting {len(tagged_chunks)} chunks to ChromaDB...")
    total = upsert_chunks(tagged_chunks)
    print(f"  ✓ {total} chunks upserted")

    # Final stats
    stats = collection_stats()
    print("\n" + "=" * 60)
    print(f"  ✅ Ingestion complete!")
    print(f"  Total chunks in DB: {stats['total_chunks']}")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Persisted at: {stats['persist_dir']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
