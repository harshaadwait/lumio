#!/bin/bash
echo "Downloading free books from Project Gutenberg..."
mkdir -p data/books

# Download plain text files
curl -s "https://www.gutenberg.org/files/2680/2680-0.txt" -o /tmp/meditations.txt
curl -s "https://www.gutenberg.org/files/45109/45109-0.txt" -o /tmp/enchiridion.txt
curl -s "https://www.gutenberg.org/files/935/935-0.txt" -o /tmp/selfhelp.txt
curl -s "https://www.gutenberg.org/files/7514/7514-0.txt" -o /tmp/stoicism.txt

# Convert to PDFs
python scripts/text_to_pdf.py /tmp/meditations.txt data/books/emotional_reactivity___meditations.pdf
python scripts/text_to_pdf.py /tmp/enchiridion.txt data/books/overthinking___the_enchiridion.pdf
python scripts/text_to_pdf.py /tmp/selfhelp.txt data/books/lack_of_motivation___self_help_smiles.pdf
python scripts/text_to_pdf.py /tmp/stoicism.txt data/books/fear_of_failure___guide_to_stoicism.pdf

echo "Running ingestion..."
python scripts/ingest_books.py
echo "Done!"
