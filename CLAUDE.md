# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## TOP RULES
MUST USE SUPERPOWER
ALWAYS SHOW ME SOME PLAN AND ALWAYS RECOMMAND THE LOWER TECH-DEBT ONE
THINK ABOUT REUSE
DONT COMMIT WITH CO-AUTHOR

## Project Overview

Academic meta-evaluation research project studying the **alignment gap between stated goals and evaluation methods** in LLM-based mental health counseling/therapy papers. The core thesis: papers claiming to build "empathetic AI therapists" often evaluate with metrics (ROUGE, BLEU, GPT-4 Likert scales) that lack psychological validity for constructs like empathy or therapeutic alliance.

**Target venues**: ACL, CHI, JMIR Mental Health.

**Language**: Research documentation and coding tables are in Chinese. The academic paper is written in English.

## Running the Extraction Tool

The only executable code is in `extract/`:

```bash
cd extract
cp .env.example .env   # Fill in OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
uv run extract.py       # Extracts metadata from PDFs in extract/paper/ → paper_metadata.csv
```

- Python 3.12, managed by `uv`
- Dependencies: `pymupdf` (PDF text), `openai` (async API calls), `python-dotenv`
- The script is idempotent: skips papers whose IDs already exist in the CSV
- Concurrency is set to 1 (`MAX_CONCURRENCY`) — adjust in `extract.py` if needed

## Research Workflow

1. **`original paper/`** — ~44 source PDFs from ACL, EMNLP, NAACL, CHI, JMIR, arXiv, etc.
2. **`extract/`** — Automated PDF metadata extraction pipeline (LLM-based)
3. **`docs/plans/pipline.md`** — Master 5-phase research plan (literature review → theoretical critique → pilot experiment → paper writing → revision)
4. **`docs/评估方法分类表...评估缺陷清单表.md`** — 7 structured coding tables for manually annotating papers (evaluation method categories, dimensions, interaction levels, prompt disclosure, theoretical grounding, inter-rater reliability, defect checklist)
5. **`docs/theme_track.xlsx`** — Theme tracking spreadsheet
6. **`paper_metadata.csv`** — Auto-extracted metadata for 52 papers (IDs 28–79)
