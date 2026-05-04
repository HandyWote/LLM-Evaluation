# Agentic Extraction Pipeline Design

Date: 2026-05-04

## Problem

The current `evaluate.py` sends the full PDF text + 39 field definitions to the LLM in a single API call. Verification of paper 1 showed **19/28 FABRICATED** evidence quotes (68%), 0 EXACT matches. The LLM prioritizes getting judgment values correct but fabricates plausible-looking evidence quotes that don't exist in the PDF.

Root cause: extracting 39 fields with verbatim evidence from a 10-15 page PDF in one shot exceeds LLM cognitive capacity. The "verbatim quote" instruction is easily overridden by the completeness imperative.

## Solution: Agentic Multi-Phase Extraction

Replace the single-shot extraction with a 6-phase agentic pipeline where the LLM:

1. Receives full PDF text as global context (once, in Phase 0)
2. Extracts fields in 6 sequential phases (5-8 fields each)
3. Uses tool calls (`search_text`, `read_page`, `verify_quote`) to locate and verify evidence
4. Auto-corrects when `verify_quote` fails (search → correct → re-verify)
5. Must complete all fields per phase before moving on (no default value filling)

### Architecture

```
extract/
├── evaluate.py          # Entry: main(), concurrency, idempotency, CSV/MD output
├── schemas.py           # Constants: CSV_COLUMNS, BOOL_FIELDS, PHASES, etc.
├── pdf_index.py         # PDFIndex class: load PDF, page indexing, search/get_page
├── tools.py             # 3 tool schemas (OpenAI function calling) + execution
├── prompts.py           # System prompt (fixed) + per-phase user message templates
└── agent_loop.py        # Core loop: message management, tool dispatch, termination
```

### Data Flow

```
evaluate.py (main)
  → PDFIndex(path)                          # Load and index PDF
  → agent_loop(client, index, paper_id)     # 6 phases sequentially
    → prompts.build_system()                # Fixed system prompt (cached)
    → prompts.build_phase_user(phase, ...)  # Per-phase user message
    → LLM call (with tools)
    → tools.execute(index, tool_call)       # Run grep/read/verify
    → Repeat until LLM returns JSON
  → parse + build_csv_row + generate_markdown  # Reuse existing logic
```

## Detailed Design

### 1. schemas.py

Extract from current `evaluate.py`:
- `CSV_COLUMNS`, `CSV_HEADER`, `INTERNAL_TO_CSV`
- `BOOL_FIELDS`, `SINGLE_CHOICE_FIELDS`, `FREE_TEXT_FIELDS`, `STRUCTURED_FIELDS`
- `METADATA_FIELDS`

New addition — `PHASES` definition:

```python
PHASES = [
    {
        "name": "元数据",
        "fields": ["title", "year", "venue", "domain"],
        "type": "metadata",  # No evidence needed, direct extraction
    },
    {
        "name": "模拟/角色建模",
        "fields": ["focus_type", "simulation_target", "persona_model_depth",
                    "uses_dynamic_state", "temporal_modeling_details"],
    },
    {
        "name": "评估方法",
        "fields": ["eval_human_experts", "eval_lay_users", "eval_user_study",
                    "eval_llm_judge", "eval_automatic"],
    },
    {
        "name": "评估核心维度",
        "fields": ["dim_safety", "dim_realism", "dim_consistency", "dim_fidelity",
                    "dim_utility", "dim_human_learning", "dim_emotional_plausibility"],
    },
    {
        "name": "评估深度与理论",
        "fields": ["raw_eval_metrics", "theory_operationalized", "behavior_eval_depth",
                    "intervention_sensitivity", "interaction_level", "prompt_disclosure",
                    "theory_grounding", "clinical_theory"],
    },
    {
        "name": "信度与质量标记",
        "fields": ["reliability_reported", "agreement_method", "coding_options",
                    "has_rubric", "llm_judge_validated", "uses_standard_metrics",
                    "metric_interpretable", "comparable_to_prior_work",
                    "has_longitudinal_eval", "has_robustness_testing",
                    "has_failure_analysis", "sim_behavior_realistic", "dataset_available"],
    },
]
```

### 2. pdf_index.py — PDFIndex

```python
@dataclass
class SearchResult:
    page: int
    text: str       # Matched snippet
    context: str    # Surrounding context (~200 chars)

class PDFIndex:
    def __init__(self, pdf_path: Path):
        """Load PDF, build per-page index and full text with --- Page N --- markers."""

    def get_full_text(self) -> str:
        """Full text with page markers. Sent once as user message in Phase 0."""

    def get_page(self, page_num: int) -> str:
        """Single page text. page_num is 1-indexed."""

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Full-text search with whitespace normalization. Returns top_k matches."""
```

### 3. tools.py — Tool Definitions & Execution

Three tools registered via OpenAI function calling:

**`search_text(query: str)`**
- Searches full PDF text for the query string
- Returns top 5 matches with page number and context
- Uses whitespace-normalized matching (handles PDF line breaks, hyphenation)

**`read_page(page_num: int)`**
- Returns full text of a specific page (1-indexed)
- For deep-reading a section the LLM identified via search

**`verify_quote(quote: str, page_num: int)`**
- Checks if `quote` appears verbatim on `page_num`
- Returns: `{"matched": true/false, "detail": "EXACT" | "closest match: ..."}`
- Whitespace normalization before matching

```python
TOOL_DEFINITIONS: list[dict] = [...]  # OpenAI function schemas

async def execute_tool(index: PDFIndex, tool_name: str, args: dict) -> str:
    """Execute a tool call and return result string for LLM."""
```

### 4. prompts.py — Prompt Strategy

**Fixed system prompt** (identical across all turns, maximizes cache hits):

Contains:
1. Role description ("你是学术论文评价方法论提取助手")
2. Tool usage instructions (when to use each tool, evidence-first strategy)
3. ALL 39 field definitions (same as current SYSTEM_PROMPT, serves as reference dictionary)
4. Output format specification (JSON structure)
5. Evidence rules (verbatim only, NOT_FOUND_IN_TEXT fallback, verify before submit)

**Per-phase user message** (changes each phase):

Phase 0 (metadata):
```
论文全文:
{full_text_with_page_markers}

请先提取元数据（title, year, venue, domain），直接返回 JSON，无需工具调用。
```

Phase 1-5:
```
现在请提取以下字段（本阶段焦点）：

- **field_name**: definition summary
- **field_name**: definition summary
...

已提取字段（可直接引用）:
{extracted_so_far JSON summary with values and pages only}

请使用工具查找和验证原文证据。完成后返回 JSON。
```

Design decision: user message repeats field definitions for current phase (for focus), even though system prompt has all definitions (for reference and caching).

### 5. agent_loop.py — Core Loop

```python
async def agent_loop(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
) -> dict | None:
    """Run 6-phase extraction with tool-use agent loop."""
```

**Per-phase flow**:
1. Build user message for current phase (field list + extracted_so_far)
2. Call LLM with `tools=TOOL_DEFINITIONS`
3. If response has tool_calls: execute them, append results, go to step 2
4. If response has no tool_calls: parse JSON, validate all fields present
5. If fields missing: append error message, go to step 2 (within same phase, counts toward turn limit)
6. If all fields present: store results, advance to next phase

**Termination conditions**:
- Max 10 turns per phase (prevent infinite loops)
- If phase hits turn limit with incomplete fields: **retry entire phase** (up to 3 times)
- If phase retry exhausted: mark paper as FAILED, skip entirely

**Turn counting**: each LLM response (whether tool call or JSON) counts as 1 turn.

**Context management**:
- All 6 phases share one conversation (messages accumulate)
- System prompt is message[0] (never changes → cache hit)
- Phase 0 user message contains full text (cached in subsequent turns)
- `extracted_so_far` passed in each phase's user message for cross-referencing

### 6. evaluate.py — Entry Point

**Reuses from current code**:
- `parse_llm_response()`, `strip_code_fences()`, `_clamp_confidence()`, `_parse_structured_field()`
- `build_csv_row()`, `generate_markdown()`, `_append_field()`
- `load_existing_ids()` (idempotency)
- `parse_id()`

**New CLI arguments**:
- `--paper ID`: process single paper
- `--log-level DEBUG|INFO`: verbosity control (default INFO)
- `--force`: re-extract even if paper already in CSV

**Concurrency model**:
- Paper-level parallelism (different papers can run concurrently via semaphore)
- Phase-level serialization (phases within one paper must be sequential, they share conversation context)
- `MAX_CONCURRENCY = 3` (configurable)

### 7. Logging Strategy

Terminal-only (no log files). Two levels:

**INFO** (default):
- Per-phase start/complete with field count and tool call count
- Per-paper summary: phases completed, total tool calls, total tokens
- Errors and retries

**DEBUG** (via `--log-level DEBUG`):
- Each tool call: name, arguments, result summary
- Each LLM response: turn number, whether tool call or JSON, token count
- Parsed field values per phase
- Verification results (matched/not matched)

Example output:
```
[Paper 1] 开始处理: 1.pdf (12 pages)
[Paper 1] Phase 1/6: 元数据 (4 fields)
[Paper 1] ✅ Phase 1 完成: 4 fields (metadata, no tools)
[Paper 1] Phase 2/6: 模拟/角色建模 (5 fields)
[Paper 1]   Turn 1: 2 tool calls (search_text, read_page)
[Paper 1]   Turn 2: 1 tool call (verify_quote → EXACT)
[Paper 1]   Turn 3: JSON returned (1834 tokens)
[Paper 1] ✅ Phase 2 完成: 5 fields (3 tool calls, 3 turns)
...
[Paper 1] 完成: 6/6 phases, 18 tool calls, 14203 tokens
```

### 8. Error Handling

| Scenario | Handling |
|----------|----------|
| PDF read failure | Print error, skip paper |
| LLM returns invalid JSON | Retry phase (up to 3 times) |
| Phase exceeds 10 turns with incomplete fields | Retry entire phase (up to 3 times) |
| Phase retry exhausted | Mark paper FAILED, skip, print missing fields |
| Tool call error (e.g. page_num out of range) | Return error message to LLM, let it adjust |
| LLM JSON missing some fields | Request supplement in same phase (counts toward turn limit) |
| API rate limit | Exponential backoff retry (reuse existing logic) |

**No default value filling.** If a phase cannot complete all fields after retries, the entire paper is marked FAILED rather than filling in defaults.

### 9. Output Format

Fully backward compatible with current output:
- `eval_results.csv`: same columns, same encoding (utf-8-sig)
- `eval_reports/{paper_id}.md`: same markdown structure
- Idempotency: same `load_existing_ids()` logic, `--force` to override

### 10. Verification Script Compatibility

The existing `verify_extraction.py` script reads `eval_reports/*.md` and checks evidence against PDFs. The new pipeline produces identical markdown format, so the verification script works without changes. Expected improvement: FABRICATED rate should drop from 68% to near 0% due to the `verify_quote` tool forcing the LLM to ground its evidence in actual text.
