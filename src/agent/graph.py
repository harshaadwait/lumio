"""
graph.py — LangGraph state machine for the Lumio AI Coach.

Flow:
  User Message
      │
      ▼
  [classify_problem]  ──► detects problem_tag from user query
      │
      ▼
  [retrieve_context]  ──► ChromaDB filtered + semantic search
      │
      ▼
  [synthesize_response]  ──► Gemini generates coaching response
      │
      ▼
  Structured CoachResponse
"""

import os
from typing import TypedDict, Optional, List, Dict, Any, Annotated
import operator

import google.generativeai as genai
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from src.vectorstore.chroma_store import query_collection
from src.book_registry import BOOK_REGISTRY, PROBLEM_TAGS, BOOK_BY_TAG

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.5-flash")
TOP_K = int(os.getenv("TOP_K_RESULTS", 5))


# ── State ──────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    user_message: str
    problem_tag: Optional[str]
    problem_label: Optional[str]
    retrieved_chunks: List[Dict[str, Any]]
    response: Optional[str]
    book_title: Optional[str]
    author: Optional[str]
    action_steps: List[str]
    error: Optional[str]


# ── Nodes ─────────────────────────────────────────────────────────────────────

def classify_problem(state: AgentState) -> AgentState:
    """
    Use Gemini to classify the user's message into one of the 13 problem tags.
    Falls back to semantic search across full corpus if classification is uncertain.
    """
    tags_list = "\n".join([
        f"- {b['problem_tag']}: {b['problem_label']} (book: {b['book_title']})"
        for b in BOOK_REGISTRY
    ])

    prompt = f"""You are a classifier for a personal development AI coach.

Given a user message, identify which ONE of the following problem tags best matches.
If none match well, respond with "unknown".

Problem tags:
{tags_list}

User message: "{state['user_message']}"

Respond with ONLY the problem_tag string (e.g., "procrastination") and nothing else.
"""

    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)
    tag = response.text.strip().lower().replace('"', '').replace("'", "")

    # Validate tag
    if tag not in PROBLEM_TAGS:
        tag = None

    book = BOOK_BY_TAG.get(tag, {}) if tag else {}

    return {
        **state,
        "problem_tag": tag,
        "problem_label": book.get("problem_label"),
        "book_title": book.get("book_title"),
        "author": book.get("author"),
    }


def retrieve_context(state: AgentState) -> AgentState:
    """
    Retrieve relevant chunks from ChromaDB.
    If problem_tag is known: filtered retrieval (targeted) + semantic fallback.
    If unknown: pure semantic retrieval across full corpus.
    """
    query = state["user_message"]
    chunks = []

    if state.get("problem_tag"):
        # Primary: filtered by problem tag
        filtered = query_collection(
            query=query,
            n_results=TOP_K,
            problem_tag=state["problem_tag"],
        )
        chunks.extend(filtered)

        # Supplementary: semantic search if filtered results are thin
        if len(filtered) < 3:
            semantic = query_collection(query=query, n_results=3)
            # Add non-duplicate chunks
            existing_ids = {c["metadata"].get("chunk_id") for c in chunks}
            for c in semantic:
                if c["metadata"].get("chunk_id") not in existing_ids:
                    chunks.append(c)
    else:
        # No tag — full corpus semantic search
        chunks = query_collection(query=query, n_results=TOP_K)

    return {**state, "retrieved_chunks": chunks}


def synthesize_response(state: AgentState) -> AgentState:
    """
    Use Gemini to generate a structured coaching response from retrieved chunks.
    """
    if not state["retrieved_chunks"]:
        return {
            **state,
            "response": "I couldn't find specific guidance for your question in my knowledge base. Could you rephrase or describe your challenge in more detail?",
            "action_steps": [],
        }

    # Build context from top chunks
    context_parts = []
    for i, chunk in enumerate(state["retrieved_chunks"][:4], 1):
        meta = chunk["metadata"]
        context_parts.append(
            f"[Source {i}: {meta.get('book_title')} by {meta.get('author')}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    book_hint = ""
    if state.get("book_title"):
        book_hint = f"The primary recommended book for this challenge is '{state['book_title']}' by {state['author']}."

    prompt = f"""You are a personal development AI coach. A user is struggling and needs guidance.

{book_hint}

Here are relevant passages from self-development books:
{context}

User's challenge: "{state['user_message']}"

Provide a coaching response that:
1. Acknowledges their specific struggle empathetically
2. Shares the core insight from the most relevant book
3. Gives 3 concrete, actionable steps they can take TODAY
4. Ends with one powerful motivational sentence

Format your response in plain conversational text. Be direct and specific, not generic.
"""

    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)

    # Extract action steps (simple heuristic)
    lines = response.text.split("\n")
    action_steps = [
        line.lstrip("0123456789.-• ").strip()
        for line in lines
        if line.strip() and any(line.strip().startswith(p) for p in ["1.", "2.", "3.", "•", "-"])
    ][:3]

    return {
        **state,
        "response": response.text.strip(),
        "action_steps": action_steps,
    }


# ── Graph Assembly ─────────────────────────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_problem", classify_problem)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("synthesize_response", synthesize_response)

    workflow.set_entry_point("classify_problem")
    workflow.add_edge("classify_problem", "retrieve_context")
    workflow.add_edge("retrieve_context", "synthesize_response")
    workflow.add_edge("synthesize_response", END)

    return workflow.compile()


# Singleton graph instance
coach_graph = build_agent_graph()


async def run_coach(user_message: str) -> Dict[str, Any]:
    """
    Entry point for the API layer.
    Returns structured coaching response.
    """
    initial_state: AgentState = {
        "user_message": user_message,
        "problem_tag": None,
        "problem_label": None,
        "retrieved_chunks": [],
        "response": None,
        "book_title": None,
        "author": None,
        "action_steps": [],
        "error": None,
    }

    final_state = await coach_graph.ainvoke(initial_state)

    return {
        "response": final_state["response"],
        "problem_detected": final_state.get("problem_label"),
        "book_recommended": final_state.get("book_title"),
        "author": final_state.get("author"),
        "action_steps": final_state.get("action_steps", []),
        "sources": [
            {
                "book": c["metadata"].get("book_title"),
                "author": c["metadata"].get("author"),
                "relevance": c["relevance_score"],
            }
            for c in final_state.get("retrieved_chunks", [])[:3]
        ],
    }
