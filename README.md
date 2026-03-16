# 💡 Lumio — AI-Powered Personal Development Coach

> Ask what you're struggling with. Lumio classifies your problem, retrieves insights from world-class books, and returns structured coaching with action steps — powered by a production-grade RAG pipeline.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange?style=flat-square)](https://trychroma.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 🎯 What Lumio Does

Most AI chatbots give generic advice. Lumio is different — it grounds every response in real book content through a 3-stage RAG pipeline:

```
User: "I keep procrastinating on my most important work"

Lumio:
  → Classifies problem: procrastination
  → Retrieves 5 relevant chunks from The War of Art (ChromaDB, filtered)
  → Synthesizes response via Gemini with action steps
  → Returns: problem tag + book attribution + 3 actions + source relevance scores
```

**Live example response:**
```json
{
  "problem_detected": "Procrastination",
  "book_recommended": "The War of Art",
  "author": "Steven Pressfield",
  "action_steps": [
    "Identify your main resistance pattern today",
    "Do one uncomfortable task in the next 20 minutes",
    "Treat creative work as a professional obligation, not a feeling"
  ],
  "sources": [
    { "book": "The War of Art", "relevance": 0.71 }
  ]
}
```

---

## 🧠 Architecture

```
                        ┌─────────────────────────────┐
                        │       FastAPI Layer          │
                        │   POST /chat  GET /books     │
                        └──────────────┬──────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │     LangGraph Agent          │
                        │                              │
                  ┌─────▼─────┐               ┌───────▼─────┐
                  │  Classify  │               │   Retrieve  │
                  │  Problem   │──────────────►│   Context   │
                  │  (Gemini)  │               │ (ChromaDB)  │
                  └───────────┘               └──────┬──────┘
                                                     │
                                       ┌─────────────▼────────────┐
                                       │    Synthesize Response    │
                                       │        (Gemini)           │
                                       └─────────────┬────────────┘
                                                     │
                                          Structured CoachResponse
```

### Key Design Decisions

**Metadata-filtered retrieval** — ChromaDB `where` filters on `problem_tag` before semantic search. A query about procrastination only retrieves chunks from procrastination-tagged books — not the entire corpus. This improves relevance precision significantly over naive top-k retrieval.

**Dual-mode fallback** — If problem classification confidence is low, Lumio falls back to full-corpus semantic search so no query goes unanswered.

**LangGraph state machine** — Three-node graph (`classify_problem` → `retrieve_context` → `synthesize_response`) with typed state. Easy to extend with memory, multi-turn conversation, or new nodes.

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|---|---|---|
| LLM | Google Gemini 1.5 Pro | Best free-tier performance for synthesis |
| Embeddings | Gemini `gemini-embedding-001` | Native integration, 768-dim vectors |
| Vector Store | ChromaDB (persistent) | Local-first, metadata filtering, cosine similarity |
| Orchestration | LangGraph | Typed state machine, easy to extend |
| API | FastAPI + Pydantic | Auto docs, type safety, async |
| PDF Parsing | PyMuPDF | Fast, accurate text extraction |

---

## 📖 Book → Problem Mapping

| Problem Tag | Book | Author |
|---|---|---|
| `emotional_reactivity` | Meditations | Marcus Aurelius ✅ |
| `overthinking` | The Enchiridion | Epictetus ✅ |
| `lack_of_motivation` | Self Help | Samuel Smiles ✅ |
| `lack_of_confidence` | The Art of Public Speaking | Dale Carnegie ✅ |
| `fear_of_failure` | A Guide to Stoicism | St. George Stock ✅ |
| `lack_of_focus` | Deep Work | Cal Newport |
| `lack_of_discipline` | Atomic Habits | James Clear |
| `procrastination` | The War of Art | Steven Pressfield |
| `feeling_lost` | Man's Search for Meaning | Viktor Frankl |
| `financial_problems` | Rich Routines | Steve Houghton |
| `emotional_money_decisions` | The Psychology of Money | Morgan Housel |
| `negative_thinking` | The Power of Positive Thinking | Norman Vincent Peale |
| `misjudging_people` | The Laws of Human Nature | Robert Greene |

✅ = currently ingested | Others = plug in your own PDFs

---

## 🚀 Quickstart

```bash
# 1. Clone
git clone https://github.com/harshaadwait/lumio.git
cd lumio

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add your GEMINI_API_KEY from aistudio.google.com (free)

# 5. Add PDFs to data/books/ using naming convention:
# {problem_tag}___{book_title}.pdf
# Example: emotional_reactivity___meditations.pdf

# 6. Ingest books
python scripts/ingest_books.py

# 7. Start API
uvicorn src.api.main:app --reload --port 8000

# 8. Test
python scripts/test_query.py "I react with anger and regret it every time"
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Main coaching query |
| `GET` | `/books` | List all 13 books + problem tags |
| `GET` | `/health` | Health check + chunk count |
| `POST` | `/ingest` | Trigger ingestion pipeline |

Interactive docs available at `http://localhost:8000/docs`

---

## 📁 Project Structure

```
lumio/
├── data/
│   └── books/                  # Place PDFs here (gitignored)
├── src/
│   ├── book_registry.py        # Central book → problem mapping
│   ├── ingestion/
│   │   ├── pdf_loader.py       # PDF → raw text (PyMuPDF)
│   │   ├── chunker.py          # Paragraph-aware chunking + overlap
│   │   └── metadata_tagger.py  # Enrich chunks with book metadata
│   ├── vectorstore/
│   │   └── chroma_store.py     # Embed + upsert + filtered query
│   ├── agent/
│   │   └── graph.py            # LangGraph 3-node state machine
│   └── api/
│       └── main.py             # FastAPI app + Pydantic schemas
├── scripts/
│   ├── ingest_books.py         # Run full ingestion pipeline
│   ├── test_query.py           # CLI test interface
│   ├── text_to_pdf.py          # Convert .txt → .pdf
│   └── html_to_pdf.py          # Convert HTML → .pdf
├── requirements.txt
└── .env.example
```

---

## 💡 Portfolio Highlights

This project demonstrates production-level RAG engineering patterns:

- **Problem-classified retrieval** — not just semantic search; Gemini classifies intent first, then ChromaDB filters by metadata tag before vector similarity
- **Typed LangGraph state machine** — `AgentState` TypedDict flows through classify → retrieve → synthesize nodes; trivial to add memory or multi-turn
- **Batch embedding with retry logic** — `tenacity` handles Gemini API rate limits during ingestion; processes in configurable batch sizes
- **Paragraph-aware chunking** — respects semantic boundaries before character limits; overlap preserves context across chunk boundaries
- **Dual-mode retrieval** — filtered (tagged) retrieval with semantic fallback ensures 100% query coverage
- **Structured API responses** — every response includes problem tag, book attribution, action steps, and source relevance scores

---

## 🔧 Configuration

All configurable via `.env`:

```env
GEMINI_API_KEY=your_key_here
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=models/gemini-embedding-001
GENERATION_MODEL=gemini-1.5-pro
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K_RESULTS=5
```

---

## 📄 License

MIT — built by [Sri Harsha Ginjupalli](https://github.com/harshaadwait)
