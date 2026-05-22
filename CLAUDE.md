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

## Commands

### Setup
```bash
cp .env.example .env   # Fill in OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
```

### Three Pipelines (all use `uv run`)

```bash
# 1. Extract basic metadata from PDFs (title, year, venue, keywords)
uv run extract

# 2. Extract evaluation methodology via 6-phase agentic pipeline
uv run evaluate
uv run evaluate --paper 1          # single paper
uv run evaluate --force            # reprocess existing
uv run evaluate --log-level DEBUG  # verbose logging

# 3. Generate AI research notes appended to eval reports
uv run note
uv run note --paper 1
uv run note --force
```

### Table Generation
```bash
cd table && uv run python generate_tables.py
```

### Tests
```bash
uv run pytest                        # all tests
uv run pytest extract/test_pdf_index.py  # single file
uv run pytest -k "test_name"         # single test
```

## Architecture

```
lib/            Shared constants, prompts, tools (imported by extract/ and evaluate/)
├── schemas.py  Field definitions, CSV columns, phase definitions (6 phases, ~40 fields)
├── prompts.py  System/user prompt builders for the agentic pipeline
└── tools.py    OpenAI function-calling tool definitions (submit_result)

extract/        PDF metadata extraction + agentic evaluation pipeline
├── extract.py  Simple metadata extractor (title/year/venue/keywords → paper_metadata.csv)
├── agent_loop.py   6-phase agentic extraction with tool-use, evidence verification, correction
├── pdf_index.py    PDF text indexing, quote verification, segmented evidence support
└── paper/      Source PDFs (gitignored)

evaluate/       Orchestrator for the agentic pipeline
└── evaluate.py Runs agent_loop on PDFs, outputs eval_results.csv + per-paper markdown reports

note/           Research note generator
└── notes.py    Appends AI-generated批判性研究笔记 to eval_reports/*.md

table/          LaTeX table generator for the academic paper
└── generate_tables.py  Reads coding CSV → ACL-format LaTeX tables

docs/           Research plans, coding tables, specs
eval_reports/   Per-paper markdown reports (generated)
compare/        Inter-rater evaluation CSVs (manual)
```

### Key Design Decisions

- **Agentic extraction** (`agent_loop.py`): 6-phase pipeline where each phase extracts a group of related fields. LLM uses `submit_result` tool to submit JSON. Post-extraction verifies evidence quotes against PDF text (positive for YES fields, negative for NO fields). Failed fields trigger a correction round.
- **Evidence verification** (`pdf_index.py`): Normalizes PDF text (fixes footnote breaks, hyphenation, whitespace) before matching. Supports segmented evidence with `...` separators.
- **Field types**: Boolean (YES/NO), single-choice (enum), free-text. All structured fields carry `{value, evidence, page, confidence}`.
- **Shared lib**: `lib/schemas.py` is the single source of truth for all field definitions, CSV column mappings, and phase groupings. Both `extract/` and `evaluate/` import from it.
- **Idempotency**: All three pipelines skip already-processed papers by default. Use `--force` to reprocess.

## Environment

- Python 3.12, managed by `uv`
- Dependencies: `pymupdf`, `openai`, `python-dotenv`, `openpyxl`
- `.env` required: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, optionally `NOTES_MODEL`
- Concurrency: `MAX_CONCURRENCY = 3` in evaluate/note, `1` in extract
