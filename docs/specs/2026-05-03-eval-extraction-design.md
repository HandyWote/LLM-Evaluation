# Design: PDF Evaluation Methodology Extractor

## Goal

Extract structured evaluation methodology information from ~100 academic PDFs (LLM-based mental health counseling papers) using an LLM with 1M context window. Output clean CSV results for analysis and per-paper Markdown reports for human verification.

## Context

- Existing `extract/extract.py` handles basic metadata extraction (title, year, venue, author) — **this tool is separate**
- 7 structured coding tables define the extraction schema (evaluation methods, core dimensions, interaction levels, prompt disclosure, theoretical grounding, reliability reporting, defect checklist)
- Full coding table definitions live in `评估方法分类表 评估核心维度表 交互层级表 提示词披露度表 理论支撑度表 信度报告表 评估缺陷清单表.md`

## Architecture

```
extract/
├── evaluate.py          # New: evaluation methodology extraction
├── extract.py           # Existing: metadata extraction (untouched)
├── .env                 # Shared API config
├── paper/               # PDF input directory
├── eval_results.csv     # New: structured results (values only)
└── eval_reports/        # New: per-paper Markdown verification docs
    ├── 28.md
    └── ...
```

## Approach: Full-paper Single-pass Extraction

Send entire paper text to LLM in one call. Each paper = one API call.

Rationale:
- 1M context window easily fits full paper text (papers are ~7K-28K tokens)
- 17 fields is manageable in a single well-structured prompt
- Simplest implementation, lowest cost per paper
- Quality ensured via evidence + confidence mechanism

## Extraction Schema

### Table 1: Evaluation Methods (YES/NO each)

| Field | Options | Judgment rule |
|-------|---------|---------------|
| `eval_human_experts` | YES/NO | Evaluators have domain expertise (therapists, clinicians, trained annotators) |
| `eval_lay_users` | YES/NO | Evaluators are non-experts (MTurk, general users) |
| `eval_user_study` | YES/NO | Structured experiment with user-system interaction |
| `eval_llm_judge` | YES/NO | LLM used to score/compare/rank outputs |
| `eval_automatic` | YES/NO | Algorithmic metrics (BLEU, ROUGE, F1, cosine similarity) |

### Table 2: Core Evaluation Dimensions (YES/NO each)

| Field | Options | Judgment rule |
|-------|---------|---------------|
| `dim_realism` | YES/NO | Assesses if output is human-like/natural |
| `dim_consistency` | YES/NO | Assesses stability across turns |
| `dim_fidelity` | YES/NO | Assesses alignment with preset persona/role |
| `dim_utility` | YES/NO | Assesses helpfulness/effectiveness |
| `dim_human_learning` | YES/NO | Measures actual human knowledge/skill change |
| `dim_emotional_plausibility` | YES/NO | Assesses empathy/emotion/affect quality |
| `dim_safety` | YES/NO | Assesses harmful/bias/ethical issues |

### Table 3: Interaction Level (single choice)

| Field | Options |
|-------|---------|
| `interaction_level` | None / Short / Extended / Longitudinal |

### Table 4: Prompt Disclosure (single choice)

| Field | Options |
|-------|---------|
| `prompt_disclosure` | Full / Partial / No |

### Table 5: Theoretical Grounding (single choice)

| Field | Options |
|-------|---------|
| `theoretical_grounding` | Strong / Weak / None |

### Table 6: Inter-rater Reliability (single choice)

| Field | Options |
|-------|---------|
| `inter_rater_reliability` | Yes / No / N/A |

### Table 7: Evaluation Defects (1-2 items from predefined list)

| Field | Options |
|-------|---------|
| `defects` | 1-2 phrases from the defect checklist (e.g., "lacks evaluation rubric", "LLM judge not validated") |

**Every field must have a value.** No blanks allowed. If evidence is weak, LLM still provides best judgment and sets confidence low.

## Per-field Metadata

Each field additionally returns:
- `evidence`: Direct quote from the paper text supporting the judgment
- `page`: Page number where evidence was found
- `confidence`: Integer 0-100

## Output Formats

### CSV (`eval_results.csv`)

Values only, no evidence/confidence. Defects separated by `|`.

```csv
id,eval_human_experts,eval_lay_users,eval_user_study,eval_llm_judge,eval_automatic,dim_realism,dim_consistency,dim_fidelity,dim_utility,dim_human_learning,dim_emotional_plausibility,dim_safety,interaction_level,prompt_disclosure,theoretical_grounding,inter_rater_reliability,defects
28,YES,NO,YES,NO,YES,NO,NO,YES,YES,NO,YES,YES,Extended,Partial,Weak,No,"lacks evaluation rubric|metric lacks interpretability"
```

### Markdown (`eval_reports/{id}.md`)

Per-field verification document with evidence and confidence:

```markdown
# Paper 28: [Title from first page]

## Table 1: Evaluation Methods

### eval_human_experts: YES (confidence: 85)
**Evidence** (p.8): "Three licensed therapists with 5+ years of clinical experience
independently rated each response on a 5-point Likert scale..."

### eval_lay_users: NO (confidence: 92)
**Evidence**: No evidence of non-expert user evaluation found in the paper.

---

## Table 2: Core Evaluation Dimensions
...
```

## Technical Details

### PDF Text Extraction

Read all pages with page markers:
```python
def extract_text_with_pages(pdf_path):
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        pages.append(f"--- Page {i+1} ---\n{page.get_text()}")
    doc.close()
    return "\n\n".join(pages)
```

### API Configuration

Reuses existing `.env`:
- `OPENAI_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

### Concurrency

- `MAX_CONCURRENCY = 3` (configurable)
- `MAX_RETRIES = 3` with exponential backoff

### Idempotency

Skip paper IDs already present in `eval_results.csv`.

### Error Handling

- PDF read failure → skip, log error
- Invalid JSON from LLM → retry up to 3 times, then mark as FAILED and continue
- All fields must have values — no blanks

### CLI Interface

```bash
cd extract
uv run evaluate.py              # Process all PDFs in paper/
uv run evaluate.py --dir /path   # Specify alternate directory
```

## Prompt Design

System prompt embeds:
1. Full judgment rules from all 7 tables
2. Strict JSON output schema
3. Instruction: every field must have a value, use evidence from text, include page numbers

User message:
- Paper full text with `--- Page N ---` markers
- Instruction to extract all fields with evidence

Output: JSON object with all fields, each containing `{value, evidence, page, confidence}`.
