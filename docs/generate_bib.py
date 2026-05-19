#!/usr/bin/env python3
"""
Generate citations.bib from citation_bibtex.csv.

Usage:
    cd docs
    uv run python3 generate_bib.py
"""

import csv
import re
from pathlib import Path


def replace_bibtex_key(bibtex: str, new_key: str) -> str:
    """Replace the key in BibTeX entry with new_key."""
    # 匹配 @type{key, 模式
    pattern = r'(@\w+\{)([^,]+)(,)'
    match = re.match(pattern, bibtex)
    if match:
        prefix = match.group(1)
        suffix = match.group(3)
        return f"{prefix}{new_key}{suffix}{bibtex[match.end():]}"
    return bibtex


def main():
    """Main entry point."""
    csv_path = Path(__file__).parent / "citation_bibtex.csv"
    bib_path = Path(__file__).parent / "citations.bib"

    print(f"Reading CSV from: {csv_path}")
    print(f"Generating BibTeX to: {bib_path}")

    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            citation_key = row.get('Citation_Key', '').strip()
            bibtex = row.get('Bibtex', '').strip()
            if bibtex and citation_key:
                # 将BibTeX中的key替换为Citation_Key
                bibtex_with_correct_key = replace_bibtex_key(bibtex, citation_key)
                entries.append(bibtex_with_correct_key)

    print(f"Found {len(entries)} BibTeX entries")

    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write("% Generated from citation_bibtex.csv\n")
        f.write(f"% Total entries: {len(entries)}\n\n")
        for i, entry in enumerate(entries, 1):
            f.write(entry)
            f.write("\n\n")

    print(f"Generated {bib_path} with {len(entries)} entries")


if __name__ == "__main__":
    main()

