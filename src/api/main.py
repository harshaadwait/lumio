"""
main.py — FastAPI application for Lumio AI Coach.

Endpoints:
  POST /chat      — Main coaching conversation
  POST /ingest    — Trigger ingestion pipeline
  GET  /books     — List all indexed books
  GET  /health    — Health check
"""

import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio

from src.agent.graph import run_coach
from src.vectorstore.chroma_store import collection_stats
from src.book_registry import BOOK_REGISTRY

app = FastAPI(
    title="Lumio AI Coach API",
    description="Lumio illuminates your blind spots using insights from 13 world-class self-development books.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=5, max_length=1000, description="User's challenge or question")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")


class SourceRef(BaseModel):
    book: str
    author: str
    relevance: float


class ChatResponse(BaseModel):
    response: str
    problem_detected: Optional[str]
    book_recommended: Optional[str]
    author: Optional[str]
    action_steps: List[str]
    sources: List[SourceRef]


class BookInfo(BaseModel):
    problem_tag: str
    problem_label: str
    book_title: str
    author: str
    core_insight: str
    action_prompt: str


class HealthResponse(BaseModel):
    status: str
    total_chunks_indexed: int
    books_registered: int


class IngestResponse(BaseModel):
    status: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check with index stats."""
    try:
        stats = collection_stats()
        return {
            "status": "healthy",
            "total_chunks_indexed": stats["total_chunks"],
            "books_registered": len(BOOK_REGISTRY),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Coach"])
async def chat(request: ChatRequest):
    """
    Main coaching endpoint.
    Classifies your problem, retrieves relevant book content,
    and returns structured coaching advice.
    """
    try:
        result = await run_coach(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coach error: {str(e)}")


@app.get("/books", response_model=List[BookInfo], tags=["Books"])
async def list_books():
    """List all 13 books in the knowledge base with their problem mappings."""
    return [
        {
            "problem_tag": b["problem_tag"],
            "problem_label": b["problem_label"],
            "book_title": b["book_title"],
            "author": b["author"],
            "core_insight": b["core_insight"],
            "action_prompt": b["action_prompt"],
        }
        for b in BOOK_REGISTRY
    ]


@app.post("/ingest", response_model=IngestResponse, tags=["System"])
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Trigger the book ingestion pipeline in the background.
    PDFs must be present in data/books/ before calling this.
    """
    def run_ingestion():
        import subprocess
        subprocess.run(["python", "scripts/ingest_books.py"], check=True)

    background_tasks.add_task(run_ingestion)
    return {
        "status": "started",
        "message": "Ingestion pipeline started in background. Check logs for progress.",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": "Lumio",
        "tagline": "Illuminate your blind spots with AI",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/chat", "/books", "/health", "/ingest"],
    }
