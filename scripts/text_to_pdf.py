"""Convert a plain text file to PDF. One-time script for Gutenberg text."""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph
def main():
    if len(sys.argv) < 3:
        print("Usage: text_to_pdf.py <input.txt> <output.pdf>")
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding="utf-8", errors="replace")

    # Skip Gutenberg header/footer (first 50 lines often boilerplate, last 100)
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if "*** START OF" in line or "***START OF" in line:
            start = i + 1
            break
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if "*** END OF" in lines[i] or "***END OF" in lines[i] or "End of Project Gutenberg" in lines[i]:
            end = i
            break
    content = "\n".join(lines[start:end])

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
