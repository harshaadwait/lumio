"""
Fetch Think and Grow Rich from sacred-texts.com (HTML chapters) and save as plain text.
Book is not on Project Gutenberg (US); sacred-texts has public domain text.
"""
import re
import sys
from pathlib import Path

import httpx

BASE = "https://sacred-texts.com/nth/tgr"
CHAPTERS = [f"tgr{i:02d}.htm" for i in range(22)]  # tgr00 .. tgr21
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def extract_text(html: str) -> str:
    """Remove HTML and leave readable text."""
    # Remove script/style
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.I)
    # Replace block elements with newlines
    html = re.sub(r"</(p|div|br|h[1-6]|li|tr)[^>]*>", "\n", html, flags=re.I)
    html = re.sub(r"<(p|div|br|h[1-6]|li|tr)[^>]*>", "\n", html, flags=re.I)
    # Remove all remaining tags
    text = re.sub(r"<[^>]+>", "", html)
    # Decode common entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/books/think_and_grow_rich.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    with httpx.Client(timeout=30.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        for i, name in enumerate(CHAPTERS):
            url = f"{BASE}/{name}"
            try:
                r = client.get(url)
                r.raise_for_status()
                text = extract_text(r.text)
                # Drop header/nav (first few lines often repeat)
                lines = text.splitlines()
                start = 0
                for j, line in enumerate(lines):
                    if line.strip().startswith("CHAPTER") or "INTRODUCTION" in line or "THINK and" in line and "GROW RICH" in line:
                        start = j
                        break
                    if "p. " in line and line.strip()[:10].replace(" ", "").replace("p.", "").isdigit():
                        start = j
                        break
                if i == 0:
                    start = 0
                parts.append("\n\n".join(lines[start:]))
                print(f"  {name} ({len(r.content)} bytes)")
            except Exception as e:
                print(f"  {name} failed: {e}", file=sys.stderr)
    full = "\n\n".join(parts)
    out_path.write_text(full, encoding="utf-8", errors="replace")
    print(f"Wrote {out_path} ({len(full)} chars)")


if __name__ == "__main__":
    main()
