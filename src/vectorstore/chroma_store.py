"""
chroma_store.py — All ChromaDB operations: embed, upsert, query.
Uses Gemini text-embedding-004 for all embeddings.
"""

import os
import time
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
COLLECTION_NAME = "lumio_books"
BATCH_SIZE = 50  # Gemini embedding API batch limit


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(client: chromadb.PersistentClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a batch of texts using Gemini text-embedding-004.
    task_type RETRIEVAL_DOCUMENT for indexing, RETRIEVAL_QUERY for queries.
    """
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="RETRIEVAL_DOCUMENT",
    )
    return result["embedding"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="RETRIEVAL_QUERY",
    )
    return result["embedding"]


def upsert_chunks(chunks: List[Dict[str, Any]]) -> int:
    """
    Embed and upsert tagged chunks into ChromaDB.
    Processes in batches to respect API rate limits.
    Returns total number of chunks upserted.
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    total = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i: i + BATCH_SIZE]

        ids = [c["chunk_id"] for c in batch]
        texts = [c["text"] for c in batch]
        metadatas = [
            {k: v for k, v in c.items() if k not in ("chunk_id", "text")}
            for c in batch
        ]

        print(f"  Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)...")
        embeddings = embed_texts(texts)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        total += len(batch)
        time.sleep(0.5)  # Rate limit courtesy pause

    return total


def query_collection(
    query: str,
    n_results: int = 5,
    problem_tag: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query ChromaDB with optional problem_tag filter.
    Returns list of result dicts with text + metadata + distance.
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    query_embedding = embed_query(query)

    where_filter = {"problem_tag": {"$eq": problem_tag}} if problem_tag else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "text": doc,
                "metadata": meta,
                "relevance_score": round(1 - dist, 4),  # cosine → similarity
            })

    return output


def collection_stats() -> Dict[str, Any]:
    """Return collection size and problem tag distribution."""
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    count = collection.count()
    return {
        "total_chunks": count,
        "collection_name": COLLECTION_NAME,
        "persist_dir": CHROMA_PERSIST_DIR,
    }
