"""Fetch a Gutenberg HTML page, extract text, and convert to PDF. Usage: html_to_pdf.py <url> <output.pdf>"""
import re
import sys
from pathlib import Path

import httpx
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph


def extract_text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.I)
    html = re.sub(r"</(p|div|br|h[1-6]|li|tr|blockquote)[^>]*>", "\n", html, flags=re.I)
    html = re.sub(r"<(p|div|br|h[1-6]|li|tr|blockquote)[^>]*>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", "", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def main():
    if len(sys.argv) < 3:
        print("Usage: html_to_pdf.py <url> <output.pdf>")
        sys.exit(1)
    url = sys.argv[1]
    dst = Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = httpx.get(url, follow_redirects=True, timeout=60)
    r.raise_for_status()
    text = extract_text(r.text)
    # Skip PG header/footer if present
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if "*** START OF" in line or "***START OF" in line:
            start = i + 1
            break
        if "Produced by" in line or "End of Project Gutenberg" in line:
            continue
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if "*** END OF" in lines[i] or "***END OF" in lines[i] or "End of Project Gutenberg" in lines[i]:
            end = i
            break
    content = "\n\n".join(lines[start:end])

    doc = SimpleDocTemplate(
        str(dst),
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
    )
    story = []
    for para in content.split("\n\n"):
        para = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if para.strip():
            story.append(Paragraph(para, body))
    doc.build(story)
    print(f"Wrote {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
