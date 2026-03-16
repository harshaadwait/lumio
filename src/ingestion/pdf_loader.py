"""
pdf_loader.py — Loads PDFs from data/books/ and extracts raw text with page metadata.
Naming convention: {problem_tag}___{book_title}.pdf
"""

import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any

BOOKS_DIR = Path("data/books")


def load_pdf(filepath: Path) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file, one dict per page.
    Returns list of: {page_num, text, source_file}
    """
    pages = []
    doc = fitz.open(str(filepath))

    for page_num, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:  # Skip blank pages
            pages.append({
                "page_num": page_num + 1,
                "text": text,
                "source_file": filepath.name,
            })

    doc.close()
    return pages


def load_all_books() -> List[Dict[str, Any]]:
    """
    Load all PDFs from data/books/.
    Parses problem_tag from filename using ___ separator.
    """
    all_pages = []

    if not BOOKS_DIR.exists():
        raise FileNotFoundError(f"Books directory not found: {BOOKS_DIR}")

    pdf_files = list(BOOKS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {BOOKS_DIR}. See README for naming convention.")

    for pdf_path in pdf_files:
        print(f"  Loading: {pdf_path.name}")

        # Parse problem_tag from filename
        parts = pdf_path.stem.split("___")
        problem_tag = parts[0] if len(parts) >= 2 else "unknown"

        pages = load_pdf(pdf_path)
        for page in pages:
            page["problem_tag"] = problem_tag

        all_pages.extend(pages)
        print(f"    → {len(pages)} pages loaded")

    return all_pages
