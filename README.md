# 💡 Lumio — Illuminate Your Blind Spots with AI

> Lumio is a production-grade RAG pipeline that maps 13 world-class self-development books to specific human challenges. Ask Lumio what you're struggling with — it finds the right book, retrieves the right insight, and gives you actionable steps. Powered by Gemini API + ChromaDB + LangGraph + FastAPI.

---

## 🧠 Architecture Overview

```
User Query
    │
    ▼
[FastAPI] ──► [LangGraph Agent]
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
  [Problem Classifier]   [Intent Router]
          │                    │
          ▼                    ▼
  [ChromaDB Retriever]  [Direct Answer]
    (metadata-filtered)
          │
          ▼
  [Gemini Synthesizer]
          │
          ▼
    Structured Response
    (book + insight + action steps)
```

---

## 📖 Book → Problem Mapping

| Problem Tag | Book | Author |
|---|---|---|
| `lack_of_focus` | Deep Work | Cal Newport |
| `negative_thinking` | The Power of Positive Thinking | Norman Vincent Peale |
| `lack_of_discipline` | Atomic Habits | James Clear |
| `lack_of_confidence` | How to Win Friends and Influence People | Dale Carnegie |
| `lack_of_motivation` | Can't Hurt Me | David Goggins |
| `fear_of_failure` | Think and Grow Rich | Napoleon Hill |
| `overthinking` | The Power of Now | Eckhart Tolle |
| `financial_problems` | Rich Routines | Steve Houghton |
| `procrastination` | The War of Art | Steven Pressfield |
| `feeling_lost` | Man's Search for Meaning | Viktor Frankl |
| `emotional_money_decisions` | The Psychology of Money | Morgan Housel |
| `misjudging_people` | The Laws of Human Nature | Robert Greene |
| `emotional_reactivity` | Meditations | Marcus Aurelius |

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM | Google Gemini 1.5 Pro |
| Embeddings | Gemini `text-embedding-004` |
| Vector Store | ChromaDB (local persistent) |
| Orchestration | LangGraph |
| API | FastAPI |
| PDF Parsing | PyMuPDF (fitz) |

---

## 🚀 Quickstart

```bash
# 1. Clone & install
git clone https://github.com/yourusername/lumio
cd lumio
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add your GEMINI_API_KEY

# 3. Add PDFs
# Place book PDFs in data/books/ following naming convention:
# {problem_tag}___{book_title}.pdf
# Example: lack_of_focus___deep_work.pdf

# 4. Ingest books into ChromaDB
python scripts/ingest_books.py

# 5. Start the API
uvicorn src.api.main:app --reload --port 8000

# 6. Test a query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I keep procrastinating on my most important work"}'
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Main coaching conversation |
| `POST` | `/ingest` | Trigger ingestion pipeline |
| `GET` | `/books` | List all indexed books |
| `GET` | `/health` | Health check |

---

## 📁 Project Structure

```
lumio/
├── data/
│   ├── books/              # Raw PDFs (gitignored)
│   └── processed/          # Chunked text cache
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py       # PDF → raw text
│   │   ├── chunker.py          # Semantic chunking
│   │   └── metadata_tagger.py  # Problem tag injection
│   ├── vectorstore/
│   │   └── chroma_store.py     # ChromaDB operations
│   ├── retrieval/
│   │   └── retriever.py        # Filtered retrieval logic
│   ├── agent/
│   │   ├── graph.py            # LangGraph state machine
│   │   └── nodes.py            # Individual agent nodes
│   └── api/
│       ├── main.py             # FastAPI app
│       └── schemas.py          # Pydantic models
├── scripts/
│   ├── ingest_books.py         # Run ingestion pipeline
│   └── test_query.py           # Test queries from CLI
├── tests/
├── requirements.txt
└── .env.example
```

---

## 📚 Sourcing Books Legally

| Book | Free Source |
|---|---|
| Meditations (Marcus Aurelius) | Project Gutenberg |
| Think and Grow Rich | Project Gutenberg |
| How to Win Friends... | Archive.org (borrowable) |
| Others | Purchase + personal use |

---

## 🎯 Portfolio Highlights

- **Metadata-filtered RAG**: Retrieval uses problem tags as ChromaDB `where` filters — not just semantic similarity
- **LangGraph state machine**: Multi-node agent with problem classification, retrieval, synthesis
- **Dual-mode retrieval**: Problem-aware (filtered) + semantic (full corpus) fallback
- **Structured responses**: Every answer returns book attribution, core insight, and action steps

---

## 📄 License

MIT
