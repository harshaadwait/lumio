# Think and Grow Rich (not on Project Gutenberg)

**Think and Grow Rich** by Napoleon Hill is **not available on Project Gutenberg** (US or Australia). Free sources that have it are behind Cloudflare or require a browser, so it can't be downloaded automatically.

## Add it manually

1. **Get the book** (choose one):
   - **Sacred-texts**: Open https://sacred-texts.com/nth/tgr/index.htm in a browser. Use "Text [Zipped]" to download `tgr.txt.gz`, then unzip to get `tgr.txt`.
   - **Internet Archive**: Search for "Think and Grow Rich Napoleon Hill" at archive.org and download a PDF or read online.

2. **If you have plain text** (`tgr.txt` or similar):
   ```bash
   python scripts/text_to_pdf.py path/to/tgr.txt data/books/fear_of_failure___think_and_grow_rich.pdf
   ```

3. **If you have a PDF**: Rename/copy it to:
   ```
   data/books/fear_of_failure___think_and_grow_rich.pdf
   ```

4. **Ingest**:
   ```bash
   python scripts/ingest_books.py
   ```

Filename must be exactly: `fear_of_failure___think_and_grow_rich.pdf` (for the Lumio problem tag `fear_of_failure`).
