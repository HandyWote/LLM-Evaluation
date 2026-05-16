# Agentic Extraction Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace single-shot PDF extraction with a 6-phase agentic pipeline that uses tool calls (search_text, read_page, verify_quote) to verify evidence quotes, reducing fabrication from 68% to near 0%.

**Architecture:** Split the current monolithic `evaluate.py` into 6 modules. Each extraction phase runs an agentic loop where the LLM uses tools to search the PDF, read pages, and verify quotes before returning JSON. All phases share one conversation for context. System prompt is cached across turns.

**Tech Stack:** Python 3.12, OpenAI Python SDK (async, function calling), PyMuPDF, pytest, pytest-asyncio

**Spec:** `docs/specs/2026-05-04-agentic-extraction-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `extract/schemas.py` | Create | Constants: CSV_COLUMNS, BOOL_FIELDS, PHASES, FIELD_DEFINITIONS |
| `extract/pdf_index.py` | Create | PDFIndex class: load PDF, per-page index, search, get_page, verify_quote |
| `extract/tools.py` | Create | 3 OpenAI tool schemas + `execute_tool()` dispatcher |
| `extract/prompts.py` | Create | Fixed system prompt + per-phase user message builders |
| `extract/agent_loop.py` | Create | Core loop: message management, tool dispatch, termination |
| `extract/evaluate.py` | Modify | Remove call_llm, import new modules, add --paper/--log-level/--force args |
| `extract/test_schemas.py` | Create | Unit tests for schemas.py |
| `extract/test_pdf_index.py` | Create | Unit tests for pdf_index.py |
| `extract/test_tools.py` | Create | Unit tests for tools.py |
| `extract/test_prompts.py` | Create | Unit tests for prompts.py |
| `extract/test_agent_loop.py` | Create | Unit tests for agent_loop.py (mocked LLM) |
| `extract/test_evaluate.py` | Modify | Update stale tests, add tests for new CLI args |

---

## Task 1: Create `schemas.py`

Extract all constants from evaluate.py into a standalone module. Add PHASES definition and FIELD_DEFINITIONS map.

**Files:**
- Create: `extract/schemas.py`
- Create: `extract/test_schemas.py`

- [ ] **Step 1: Write `schemas.py`**

```python
"""Constants and field definitions for the agentic extraction pipeline."""

# --- CSV Column Mapping (internal_name -> theme_track.csv header, order matters) ---
CSV_COLUMNS = [
    ("paper_id", "Paper_ID"),
    ("title", "Title"),
    ("year", "Year"),
    ("venue", "Venue"),
    ("domain", "Domain"),
    ("focus_type", "Focus_Type"),
    ("simulation_target", "Simulation_Target"),
    ("persona_model_depth", "Persona_Model_Depth"),
    ("uses_dynamic_state", "Uses_Dynamic_State"),
    ("temporal_modeling_details", "Temporal_Modeling_Details"),
    ("eval_human_experts", "Eval_Human_Experts"),
    ("eval_lay_users", "Eval_Lay_Users"),
    ("eval_user_study", "Eval_User_Study"),
    ("eval_llm_judge", "Eval_LLM_Judge"),
    ("eval_automatic", "Eval_Automatic"),
    ("dim_safety", "Safety"),
    ("dim_realism", "Realism"),
    ("dim_consistency", "Consistency"),
    ("dim_fidelity", "Fidelity"),
    ("dim_human_learning", "Human Learning / Outcomes"),
    ("dim_utility", "Utility"),
    ("dim_emotional_plausibility", "Emotional Plausibility"),
    ("raw_eval_metrics", "Raw Eval Metrics"),
    ("theory_operationalized", "Theory_Operationalized"),
    ("behavior_eval_depth", "Behavior_Eval_Depth"),
    ("intervention_sensitivity", "Intervention_Sensitivity"),
    ("interaction_level", "Interaction_Level"),
    ("prompt_disclosure", "Prompt_Disclosure"),
    ("theory_grounding", "Theory_Grounding"),
    ("clinical_theory", "Clinical_Theory"),
    ("reliability_reported", "Reliability_Reported"),
    ("agreement_method", "Agreement Method"),
    ("coding_options", "Coding Options"),
    ("has_rubric", "Has_Rubric"),
    ("llm_judge_validated", "LLM_Judge_Validated"),
    ("uses_standard_metrics", "Uses_Standard_Metrics"),
    ("metric_interpretable", "Metric_Interpretable"),
    ("comparable_to_prior_work", "Comparable_To_Prior_Work"),
    ("has_longitudinal_eval", "Has_Longitudinal_Eval"),
    ("has_robustness_testing", "Has_Robustness_Testing"),
    ("has_failure_analysis", "Has_Failure_Analysis"),
    ("sim_behavior_realistic", "Sim_Behavior_Realistic"),
    ("dataset_available", "Dataset_Available"),
]

CSV_HEADER = [csv_name for _, csv_name in CSV_COLUMNS]
INTERNAL_TO_CSV = dict(CSV_COLUMNS)

# --- Field Groups ---

METADATA_FIELDS = ["title", "year", "venue", "domain"]

BOOL_FIELDS = [
    "eval_human_experts", "eval_lay_users", "eval_user_study",
    "eval_llm_judge", "eval_automatic",
    "dim_realism", "dim_consistency", "dim_fidelity",
    "dim_utility", "dim_human_learning", "dim_emotional_plausibility", "dim_safety",
    "uses_dynamic_state", "intervention_sensitivity",
    "has_rubric", "llm_judge_validated", "uses_standard_metrics",
    "metric_interpretable", "comparable_to_prior_work",
    "has_longitudinal_eval", "has_robustness_testing",
    "has_failure_analysis", "sim_behavior_realistic", "dataset_available",
]

SINGLE_CHOICE_FIELDS = {
    "simulation_target": ["Client Agent", "Therapist Agent", "Dual-Agent", "Human Trainee"],
    "persona_model_depth": [
        "Surface Persona", "Behavioral State Model",
        "Cognitive Model", "Dynamic Traits", "Expert Principles",
    ],
    "theory_operationalized": ["None", "Partial", "Strong"],
    "behavior_eval_depth": ["Dynamic", "Static", "None"],
    "interaction_level": ["None", "Short", "Extended", "Longitudinal"],
    "prompt_disclosure": ["Full", "Partial", "No"],
    "theory_grounding": ["Strong", "Weak", "None"],
    "reliability_reported": ["Yes", "No", "N/A"],
    "coding_options": ["Yes", "No", "N/A"],
}

FREE_TEXT_FIELDS = [
    "focus_type", "temporal_modeling_details", "raw_eval_metrics",
    "clinical_theory", "agreement_method",
]

STRUCTURED_FIELDS = BOOL_FIELDS + list(SINGLE_CHOICE_FIELDS.keys()) + FREE_TEXT_FIELDS

# --- Phase Definitions ---

PHASES = [
    {
        "name": "元数据",
        "fields": ["title", "year", "venue", "domain"],
        "type": "metadata",
    },
    {
        "name": "模拟/角色建模",
        "fields": [
            "focus_type", "simulation_target", "persona_model_depth",
            "uses_dynamic_state", "temporal_modeling_details",
        ],
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

# --- Field Definitions (for prompts) ---
# Maps field name -> short definition string used in per-phase user messages.

FIELD_DEFINITIONS = {
    "title": "论文标题（原文）",
    "year": "发表年份（数字）",
    "venue": "发表场所（会议名/期刊名）",
    "domain": "研究领域（如 Counseling, Therapy, Mental Health 等）",
    "focus_type": "论文的主要研究焦点类型（开放分类）。如 SimulationFramework, EvaluationFramework, Dataset 等",
    "simulation_target": "模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee",
    "persona_model_depth": "模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles",
    "uses_dynamic_state": "是否使用动态状态建模（YES/NO）",
    "temporal_modeling_details": "动态状态建模的具体方式描述",
    "eval_human_experts": "领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）",
    "eval_lay_users": "非专家/普通用户进行评估（YES/NO）",
    "eval_user_study": "结构化实验，用户与系统发生交互（YES/NO）",
    "eval_llm_judge": "使用大模型进行打分、比较、排序（YES/NO）",
    "eval_automatic": "算法/数学公式自动计算的指标（YES/NO）",
    "dim_safety": "是否避免有害/偏见输出（YES/NO）",
    "dim_realism": "输出是否像人类或自然（YES/NO）",
    "dim_consistency": "跨轮次行为是否稳定（YES/NO）",
    "dim_fidelity": "是否符合预设角色/目标（YES/NO）",
    "dim_utility": "对任务是否有用/有效（YES/NO）",
    "dim_human_learning": "是否带来人类进步/改变（YES/NO）",
    "dim_emotional_plausibility": "情绪反应是否真实/恰当（YES/NO）",
    "raw_eval_metrics": "实际使用的评估指标名称（自由文本）",
    "theory_operationalized": "理论操作化程度: None / Partial / Strong",
    "behavior_eval_depth": "行为变化评估深度: Dynamic / Static / None",
    "intervention_sensitivity": "系统行为是否根据输入发生适当变化（YES/NO）",
    "interaction_level": "对话上下文深度: None / Short / Extended / Longitudinal",
    "prompt_disclosure": "提示词披露程度: Full / Partial / No",
    "theory_grounding": "评估标准与理论挂钩程度: Strong / Weak / None",
    "clinical_theory": "具体使用的临床理论或框架名称（自由文本）",
    "reliability_reported": "是否报告了评估者间信度: Yes / No / N/A",
    "agreement_method": "具体使用的一致性评测方法（自由文本，若无则空字符串）",
    "coding_options": "是否明确报告了评估者之间的一致性: Yes / No / N/A",
    "has_rubric": "是否提供了明确的评分标准/评分指引（YES/NO）",
    "llm_judge_validated": "LLM裁判是否经过验证（YES/NO）",
    "uses_standard_metrics": "是否使用了标准/公认的评估指标（YES/NO）",
    "metric_interpretable": "评估指标的含义是否清晰可解释（YES/NO）",
    "comparable_to_prior_work": "评估是否可与先前研究进行对比（YES/NO）",
    "has_longitudinal_eval": "是否包含纵向/长期评估（YES/NO）",
    "has_robustness_testing": "是否在不同条件下进行了鲁棒性测试（YES/NO）",
    "has_failure_analysis": "是否分析了失败案例（YES/NO）",
    "sim_behavior_realistic": "模拟行为是否真实（YES/NO）",
    "dataset_available": "数据集是否公开可用（YES/NO）",
}
```

- [ ] **Step 2: Write `test_schemas.py`**

```python
"""Tests for schemas.py constants."""

import pytest
from schemas import (
    CSV_COLUMNS, CSV_HEADER, INTERNAL_TO_CSV,
    METADATA_FIELDS, BOOL_FIELDS, SINGLE_CHOICE_FIELDS,
    FREE_TEXT_FIELDS, STRUCTURED_FIELDS,
    PHASES, FIELD_DEFINITIONS,
)


def test_csv_columns_count():
    assert len(CSV_COLUMNS) == 44


def test_csv_header_matches_columns():
    assert CSV_HEADER == [csv_name for _, csv_name in CSV_COLUMNS]


def test_internal_to_csv_round_trip():
    for internal, csv_name in CSV_COLUMNS:
        assert INTERNAL_TO_CSV[internal] == csv_name


def test_metadata_fields_in_columns():
    for f in METADATA_FIELDS:
        assert f in INTERNAL_TO_CSV


def test_bool_fields_all_yes_no():
    assert "eval_human_experts" in BOOL_FIELDS
    assert len(BOOL_FIELDS) == 23


def test_single_choice_fields_have_options():
    for field, options in SINGLE_CHOICE_FIELDS.items():
        assert len(options) >= 2
        assert field in INTERNAL_TO_CSV


def test_structured_fields_covers_all_non_metadata():
    all_schema_fields = set(BOOL_FIELDS) | set(SINGLE_CHOICE_FIELDS.keys()) | set(FREE_TEXT_FIELDS)
    assert set(STRUCTURED_FIELDS) == all_schema_fields
    assert "title" not in STRUCTURED_FIELDS
    assert "year" not in STRUCTURED_FIELDS


def test_phases_count():
    assert len(PHASES) == 6


def test_phases_cover_all_fields():
    phase_fields = []
    for phase in PHASES:
        phase_fields.extend(phase["fields"])
    assert len(phase_fields) == len(set(phase_fields)), "Duplicate field across phases"
    all_fields = set(METADATA_FIELDS) | set(STRUCTURED_FIELDS)
    assert set(phase_fields) == all_fields, f"Missing: {all_fields - set(phase_fields)}"


def test_phase_0_is_metadata():
    assert PHASES[0]["type"] == "metadata"
    assert set(PHASES[0]["fields"]) == set(METADATA_FIELDS)


def test_field_definitions_cover_all_fields():
    all_fields = set(METADATA_FIELDS) | set(STRUCTURED_FIELDS)
    assert set(FIELD_DEFINITIONS.keys()) == all_fields


def test_field_definitions_no_empty_strings():
    for field, defn in FIELD_DEFINITIONS.items():
        assert defn, f"Empty definition for {field}"
```

- [ ] **Step 3: Run tests**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_schemas.py -v`
Expected: All 12 tests PASS

- [ ] **Step 4: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/schemas.py extract/test_schemas.py
git commit -m "feat: add schemas module with constants, PHASES, and FIELD_DEFINITIONS"
```

---

## Task 2: Create `pdf_index.py`

PDFIndex class: load PDF, build per-page index, provide search/get_page/verify_quote.

**Files:**
- Create: `extract/pdf_index.py`
- Create: `extract/test_pdf_index.py`

- [ ] **Step 1: Write `test_pdf_index.py`**

```python
"""Tests for pdf_index.py."""

import pytest
from pathlib import Path
from pdf_index import PDFIndex, SearchResult


PAPER_DIR = Path(__file__).parent / "paper"


@pytest.fixture
def index():
    pdf_path = PAPER_DIR / "1.pdf"
    if not pdf_path.exists():
        pytest.skip("1.pdf not found in paper/")
    return PDFIndex(pdf_path)


class TestPDFIndexBasics:
    def test_page_count(self, index):
        assert index.page_count > 0

    def test_get_full_text_contains_page_markers(self, index):
        text = index.get_full_text()
        assert "--- Page 1 ---" in text

    def test_get_page_returns_string(self, index):
        page = index.get_page(1)
        assert isinstance(page, str)
        assert len(page) > 0

    def test_get_page_out_of_range(self, index):
        result = index.get_page(999)
        assert "Error" in result

    def test_get_page_one_indexed(self, index):
        page1 = index.get_page(1)
        page2 = index.get_page(2)
        assert page1 != page2


class TestSearch:
    def test_search_returns_results(self, index):
        results = index.search("evaluation", top_k=3)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, SearchResult)
            assert isinstance(r.page, int)
            assert 1 <= r.page <= index.page_count
            assert isinstance(r.text, str)
            assert isinstance(r.context, str)

    def test_search_empty_query(self, index):
        results = index.search("", top_k=5)
        assert results == []

    def test_search_no_match(self, index):
        results = index.search("xyznonexistentterm12345", top_k=5)
        assert results == []

    def test_search_respects_top_k(self, index):
        results = index.search("the", top_k=2)
        assert len(results) <= 2


class TestVerifyQuote:
    def test_verify_exact_match(self, index):
        page_text = index.get_page(1)
        # Take first 50 chars as a known quote
        quote = page_text[:50].strip()
        result = index.verify_quote(quote, 1)
        assert result["matched"] is True
        assert result["detail"] == "EXACT"

    def test_verify_no_match(self, index):
        result = index.verify_quote("this text definitely does not exist in any paper", 1)
        assert result["matched"] is False

    def test_verify_wrong_page(self, index):
        page1_text = index.get_page(1)
        if index.page_count < 2:
            pytest.skip("Need at least 2 pages")
        page2_text = index.get_page(2)
        # Find text unique to page 1 and search on page 2
        quote = page1_text[:80].strip()
        result = index.verify_quote(quote, 2)
        assert result["matched"] is False

    def test_verify_page_out_of_range(self, index):
        result = index.verify_quote("some text", 999)
        assert result["matched"] is False
        assert "out of range" in result["detail"]

    def test_verify_whitespace_normalization(self, index):
        page_text = index.get_page(1)
        # Insert extra whitespace into the quote
        quote = page_text[:50].strip()
        modified = quote[:25] + "  \n  " + quote[25:]
        result = index.verify_quote(modified, 1)
        assert result["matched"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_pdf_index.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write `pdf_index.py`**

```python
"""PDF indexing and text search for the agentic extraction pipeline."""

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz


@dataclass
class SearchResult:
    page: int
    text: str
    context: str


def _normalize_whitespace(s: str) -> str:
    return re.sub(r'\s+', ' ', s.strip().lower())


class PDFIndex:
    def __init__(self, pdf_path: Path):
        self._pages: list[str] = []
        self._full_text: str = ""
        doc = fitz.open(str(pdf_path))
        parts = []
        for page in doc:
            text = page.get_text()
            self._pages.append(text)
            parts.append(f"--- Page {len(self._pages)} ---\n{text}")
        doc.close()
        self._full_text = "\n\n".join(parts)

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def get_full_text(self) -> str:
        return self._full_text

    def get_page(self, page_num: int) -> str:
        if 1 <= page_num <= len(self._pages):
            return self._pages[page_num - 1]
        return f"Error: Page {page_num} out of range (1-{len(self._pages)})"

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query = query.strip()
        if not query:
            return []
        terms = query.split()
        pattern = r'\s+'.join(re.escape(t) for t in terms)
        regex = re.compile(pattern, re.IGNORECASE)
        results: list[SearchResult] = []
        for i, page_text in enumerate(self._pages):
            for match in regex.finditer(page_text):
                matched_text = match.group()
                start, end = match.span()
                ctx_start = max(0, start - 100)
                ctx_end = min(len(page_text), end + 100)
                context = page_text[ctx_start:ctx_end]
                results.append(SearchResult(
                    page=i + 1,
                    text=matched_text,
                    context=context,
                ))
        return results[:top_k]

    def verify_quote(self, quote: str, page_num: int) -> dict:
        if page_num < 1 or page_num > len(self._pages):
            return {"matched": False, "detail": f"Page {page_num} out of range (1-{len(self._pages)})"}
        page_text = self._pages[page_num - 1]
        normalized_page = _normalize_whitespace(page_text)
        normalized_quote = _normalize_whitespace(quote)
        if not normalized_quote:
            return {"matched": False, "detail": "Empty quote"}
        if normalized_quote in normalized_page:
            return {"matched": True, "detail": "EXACT"}
        sentences = re.split(r'(?<=[.!?])\s+', page_text)
        best_ratio = 0.0
        best_match = ""
        for sent in sentences:
            ratio = difflib.SequenceMatcher(None, _normalize_whitespace(sent), normalized_quote).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = sent
        if best_ratio > 0.5:
            return {"matched": False, "detail": f"closest match (similarity {best_ratio:.0%}): {best_match[:200]}"}
        return {"matched": False, "detail": "No similar text found on this page"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_pdf_index.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/pdf_index.py extract/test_pdf_index.py
git commit -m "feat: add PDFIndex with search and verify_quote"
```

---

## Task 3: Create `tools.py`

Three OpenAI function-calling tool definitions + `execute_tool()` dispatcher.

**Files:**
- Create: `extract/tools.py`
- Create: `extract/test_tools.py`

- [ ] **Step 1: Write `test_tools.py`**

```python
"""Tests for tools.py."""

import json
import pytest
from unittest.mock import MagicMock

from pdf_index import PDFIndex
from tools import TOOL_DEFINITIONS, execute_tool


class MockIndex:
    def __init__(self):
        self._pages = [
            "This is page one. It discusses evaluation methods.\nThe paper uses BLEU and ROUGE for evaluation.",
            "Page two covers safety and realism.\nThey found that the model produces harmful output 5% of the time.",
            "Page three is about conclusion.\nThe authors recommend further work on empathy.",
        ]

    @property
    def page_count(self):
        return len(self._pages)

    def get_page(self, page_num):
        if 1 <= page_num <= len(self._pages):
            return self._pages[page_num - 1]
        return f"Error: Page {page_num} out of range"

    def search(self, query, top_k=5):
        results = []
        for i, text in enumerate(self._pages):
            if query.lower() in text.lower():
                results.append({"page": i + 1, "text": query, "context": text[:200]})
        return results

    def verify_quote(self, quote, page_num):
        page = self.get_page(page_num)
        if "Error" in page:
            return {"matched": False, "detail": page}
        if quote in page:
            return {"matched": True, "detail": "EXACT"}
        return {"matched": False, "detail": "No similar text found"}


@pytest.fixture
def idx():
    return MockIndex()


def test_tool_definitions_exist():
    assert len(TOOL_DEFINITIONS) == 3
    names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    assert names == {"search_text", "read_page", "verify_quote"}


def test_tool_definitions_have_parameters():
    for tool in TOOL_DEFINITIONS:
        func = tool["function"]
        assert "parameters" in func
        assert func["parameters"]["type"] == "object"


def test_execute_search_text(idx):
    result = execute_tool(idx, "search_text", {"query": "evaluation"})
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_execute_read_page(idx):
    result = execute_tool(idx, "read_page", {"page_num": 1})
    assert "This is page one" in result


def test_execute_read_page_out_of_range(idx):
    result = execute_tool(idx, "read_page", {"page_num": 99})
    assert "Error" in result


def test_execute_verify_quote_match(idx):
    result = execute_tool(idx, "verify_quote", {"quote": "evaluation methods", "page_num": 1})
    parsed = json.loads(result)
    assert parsed["matched"] is True


def test_execute_verify_quote_no_match(idx):
    result = execute_tool(idx, "verify_quote", {"quote": "nonexistent text", "page_num": 1})
    parsed = json.loads(result)
    assert parsed["matched"] is False


def test_execute_unknown_tool(idx):
    result = execute_tool(idx, "unknown_tool", {})
    assert "Error" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_tools.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write `tools.py`**

```python
"""Tool definitions (OpenAI function calling) and execution for the agentic extraction pipeline."""

import json
from pdf_index import PDFIndex, SearchResult

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Search the full PDF text for a query string. Returns top 5 matches with page number and surrounding context. Use this to locate relevant sections before reading.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The text to search for in the PDF.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Return the full text of a specific page. Page numbers are 1-indexed. Use this to read a section in detail after locating it via search_text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_num": {
                        "type": "integer",
                        "description": "The page number to read (1-indexed).",
                    },
                },
                "required": ["page_num"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_quote",
            "description": "Check if a quote appears verbatim on a specific page. Returns whether the quote matches exactly, approximately, or not at all. Always verify evidence quotes before submitting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote": {
                        "type": "string",
                        "description": "The quote to verify.",
                    },
                    "page_num": {
                        "type": "integer",
                        "description": "The page number where the quote should appear (1-indexed).",
                    },
                },
                "required": ["quote", "page_num"],
            },
        },
    },
]


def execute_tool(index: PDFIndex, tool_name: str, args: dict) -> str:
    """Execute a tool call and return a JSON string result for the LLM."""
    if tool_name == "search_text":
        query = args.get("query", "")
        results = index.search(query)
        return json.dumps([
            {"page": r.page, "text": r.text, "context": r.context}
            for r in results
        ])
    elif tool_name == "read_page":
        page_num = args.get("page_num", 1)
        text = index.get_page(page_num)
        return json.dumps({"page": page_num, "text": text})
    elif tool_name == "verify_quote":
        quote = args.get("quote", "")
        page_num = args.get("page_num", 1)
        result = index.verify_quote(quote, page_num)
        return json.dumps(result)
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_tools.py -v`
Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/tools.py extract/test_tools.py
git commit -m "feat: add tool definitions and execute_tool dispatcher"
```

---

## Task 4: Create `prompts.py`

Fixed system prompt (cached) + per-phase user message builders.

**Files:**
- Create: `extract/prompts.py`
- Create: `extract/test_prompts.py`

- [ ] **Step 1: Write `test_prompts.py`**

```python
"""Tests for prompts.py."""

import pytest
from prompts import build_system_prompt, build_phase_user_message


class TestBuildSystemPrompt:
    def test_contains_role_description(self):
        prompt = build_system_prompt()
        assert "学术论文评价方法论提取助手" in prompt

    def test_contains_tool_instructions(self):
        prompt = build_system_prompt()
        assert "search_text" in prompt
        assert "read_page" in prompt
        assert "verify_quote" in prompt

    def test_contains_evidence_rules(self):
        prompt = build_system_prompt()
        assert "verbatim" in prompt.lower() or "逐字" in prompt

    def test_contains_all_field_definitions(self):
        from schemas import METADATA_FIELDS, STRUCTURED_FIELDS
        prompt = build_system_prompt()
        for field in METADATA_FIELDS + STRUCTURED_FIELDS:
            assert field in prompt, f"Field {field} not in system prompt"

    def test_contains_json_format(self):
        prompt = build_system_prompt()
        assert "JSON" in prompt


class TestBuildPhaseUserMessage:
    def test_phase_0_contains_full_text(self):
        full_text = "--- Page 1 ---\nSample content"
        msg = build_phase_user_message(0, full_text=full_text, extracted_so_far={})
        assert "--- Page 1 ---" in msg

    def test_phase_0_contains_metadata_instruction(self):
        msg = build_phase_user_message(0, full_text="text", extracted_so_far={})
        assert "元数据" in msg

    def test_phase_1_contains_field_names(self):
        from schemas import PHASES
        msg = build_phase_user_message(1, full_text="text", extracted_so_far={})
        for field in PHASES[1]["fields"]:
            assert field in msg

    def test_phase_1_contains_tool_instruction(self):
        msg = build_phase_user_message(1, full_text="text", extracted_so_far={})
        assert "工具" in msg or "tool" in msg.lower()

    def test_later_phase_contains_extracted_so_far(self):
        extracted = {"title": "Test Paper", "year": 2024}
        msg = build_phase_user_message(2, full_text="text", extracted_so_far=extracted)
        assert "Test Paper" in msg

    def test_all_phases_produce_non_empty_messages(self):
        for phase_idx in range(6):
            msg = build_phase_user_message(phase_idx, full_text="text", extracted_so_far={})
            assert len(msg) > 50, f"Phase {phase_idx} message too short"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_prompts.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Write `prompts.py`**

```python
"""Prompt construction for the agentic extraction pipeline."""

import json
from schemas import PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS


def build_system_prompt() -> str:
    return """\
你是一个学术论文评价方法论提取助手。从给定的论文全文中提取结构化信息。

## 工具使用规则

你有三个工具可用：
1. **search_text(query)** — 搜索论文全文，返回最相关的匹配和页码。先用它定位相关章节。
2. **read_page(page_num)** — 读取指定页面的完整文本。找到相关页后用它精读。
3. **verify_quote(quote, page_num)** — 验证引用是否在指定页面上逐字出现。**必须**在提交证据前验证每个引用。

**证据提取策略：**
- 先用 search_text 定位相关内容 → 用 read_page 精读 → 提取引用 → 用 verify_quote 验证
- 如果 verify_quote 显示不匹配，重新搜索并提取正确的引用
- 禁止编造、改写或概括引用。evidence 必须是论文原文的逐字引用。

## 字段定义（完整参考）

以下是所有可提取的字段。每个阶段你只需提取当前阶段指定的字段，但可以参考其他字段的定义来理解上下文。

""" + _build_field_definitions_section() + "\n" + _build_output_format_section()


def _build_field_definitions_section() -> str:
    lines = []
    for phase in PHASES:
        lines.append(f"### {phase['name']}")
        for field in phase["fields"]:
            lines.append(f"- **{field}**: {FIELD_DEFINITIONS[field]}")
        lines.append("")
    return "\n".join(lines)


def _build_output_format_section() -> str:
    return """\
## 输出格式

严格返回 JSON 对象。

元数据字段（title, year, venue, domain）直接返回值。

其余字段格式：
```json
{
  "field_name": {"value": "...", "evidence": "...", "page": 1, "confidence": 80}
}
```

规则：
- 每个字段都必须有值（agreement_method 可以是空字符串 ""）
- 布尔字段 value 为 "YES" 或 "NO"
- confidence 为 0-100 整数
- evidence 必须是论文原文的逐字引用，提交前用 verify_quote 验证
- NO 字段的 evidence 写 "No evidence of [具体方法/维度] found in the paper."
- page 为页码数字，若无则 null
"""


def build_phase_user_message(
    phase_idx: int,
    full_text: str,
    extracted_so_far: dict,
) -> str:
    phase = PHASES[phase_idx]

    if phase.get("type") == "metadata":
        return f"""论文全文:
{full_text}

请先提取元数据（{', '.join(phase['fields'])}），直接返回 JSON，无需工具调用。"""

    field_list = "\n".join(
        f"- **{f}**: {FIELD_DEFINITIONS[f]}" for f in phase["fields"]
    )

    extracted_summary = ""
    if extracted_so_far:
        lines = []
        for key, val in extracted_so_far.items():
            if isinstance(val, dict):
                page_info = f" (p.{val['page']})" if val.get("page") else ""
                lines.append(f"  - {key}: {val['value']}{page_info}")
            else:
                lines.append(f"  - {key}: {val}")
        extracted_summary = "\n已提取字段（可直接引用）:\n" + "\n".join(lines)

    return f"""现在请提取以下字段（阶段 {phase_idx}/{len(PHASES) - 1}: {phase['name']}）：

{field_list}
{extracted_summary}

请使用工具查找和验证原文证据。对每个 YES 字段，必须用 verify_quote 验证证据引用。完成后返回仅包含本阶段字段的 JSON。"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_prompts.py -v`
Expected: All 12 tests PASS

- [ ] **Step 5: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/prompts.py extract/test_prompts.py
git commit -m "feat: add prompt builders for agentic extraction pipeline"
```

---

## Task 5: Create `agent_loop.py`

Core agentic loop: message management, tool dispatch, phase transitions, termination.

**Files:**
- Create: `extract/agent_loop.py`
- Create: `extract/test_agent_loop.py`
- Modify: `extract/pyproject.toml` (add pytest-asyncio)

- [ ] **Step 1: Add pytest-asyncio dependency**

Edit `extract/pyproject.toml`, change:
```toml
[dependency-groups]
dev = ["pytest>=8.0"]
```
to:
```toml
[dependency-groups]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24"]
```

Then install: `cd /home/handy/Projects/LLM-Evaluate/extract && uv sync`

- [ ] **Step 2: Write `test_agent_loop.py`**

```python
"""Tests for agent_loop.py — uses mocked AsyncOpenAI client."""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from schemas import PHASES
from pdf_index import PDFIndex
from agent_loop import agent_loop


def _make_json_message(content: str):
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = None
    return msg


def _make_tool_call_message(tool_calls: list[dict]):
    msg = MagicMock()
    msg.content = None
    msg.tool_calls = []
    for tc in tool_calls:
        mock_tc = MagicMock()
        mock_tc.id = tc["id"]
        mock_tc.type = "function"
        mock_tc.function.name = tc["name"]
        mock_tc.function.arguments = tc["args"]
        msg.tool_calls.append(mock_tc)
    return msg


def _make_response(message):
    resp = MagicMock()
    resp.choices = [MagicMock(message=message)]
    resp.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    return resp


class MockIndex:
    def __init__(self):
        self._pages = ["Page 1 text about evaluation.\nIt uses BLEU.", "Page 2 text about safety."]

    @property
    def page_count(self):
        return len(self._pages)

    def get_full_text(self):
        return "--- Page 1 ---\nPage 1 text about evaluation.\nIt uses BLEU.\n\n--- Page 2 ---\nPage 2 text about safety."

    def get_page(self, page_num):
        return self._pages[page_num - 1] if 1 <= page_num <= len(self._pages) else "Error"

    def search(self, query, top_k=5):
        return [{"page": 1, "text": query, "context": self._pages[0][:100]}] if "evaluation" in query.lower() else []

    def verify_quote(self, quote, page_num):
        return {"matched": True, "detail": "EXACT"} if quote in self._pages[page_num - 1] else {"matched": False, "detail": "No match"}


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client


@pytest.fixture
def semaphore():
    return asyncio.Semaphore(3)


def _metadata_json():
    return json.dumps({"title": "Test Paper", "year": 2024, "venue": "ACL", "domain": "Counseling"})


def _phase1_json():
    return json.dumps({
        "focus_type": {"value": "EvaluationFramework", "evidence": "evaluation framework", "page": 1, "confidence": 80},
        "simulation_target": {"value": "Client Agent", "evidence": "simulates client", "page": 1, "confidence": 75},
        "persona_model_depth": {"value": "Surface Persona", "evidence": "surface persona", "page": 1, "confidence": 70},
        "uses_dynamic_state": {"value": "NO", "evidence": "No evidence found in the paper.", "page": None, "confidence": 80},
        "temporal_modeling_details": {"value": "", "evidence": "No evidence found in the paper.", "page": None, "confidence": 80},
    })


@pytest.mark.asyncio
async def test_phase0_metadata_no_tools(mock_client, semaphore):
    mock_client.chat.completions.create = AsyncMock(
        return_value=_make_response(_make_json_message(_metadata_json()))
    )
    index = MockIndex()
    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", index)
    assert result is not None
    assert result["title"] == "Test Paper"
    assert result["year"] == 2024


@pytest.mark.asyncio
async def test_phase1_with_tool_calls(mock_client, semaphore):
    idx = MockIndex()

    responses = [
        _make_response(_make_json_message(_metadata_json())),
        _make_response(_make_tool_call_message([
            {"id": "call_1", "name": "search_text", "args": '{"query": "evaluation"}'},
        ])),
        _make_response(_make_json_message(_phase1_json())),
    ]
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    assert result["focus_type"]["value"] == "EvaluationFramework"


@pytest.mark.asyncio
async def test_phase_retry_on_missing_fields(mock_client, semaphore):
    idx = MockIndex()

    incomplete_json = json.dumps({
        "focus_type": {"value": "EvaluationFramework", "evidence": "ev", "page": 1, "confidence": 80},
    })

    full_json = json.dumps({
        "focus_type": {"value": "EvaluationFramework", "evidence": "ev", "page": 1, "confidence": 80},
        "simulation_target": {"value": "Client Agent", "evidence": "sim", "page": 1, "confidence": 75},
        "persona_model_depth": {"value": "Surface Persona", "evidence": "sp", "page": 1, "confidence": 70},
        "uses_dynamic_state": {"value": "NO", "evidence": "No evidence found in the paper.", "page": None, "confidence": 80},
        "temporal_modeling_details": {"value": "", "evidence": "No evidence found in the paper.", "page": None, "confidence": 80},
    })

    responses = [
        _make_response(_make_json_message(_metadata_json())),
        _make_response(_make_json_message(incomplete_json)),
        _make_response(_make_json_message(full_json)),
    ]
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    assert "simulation_target" in result


@pytest.mark.asyncio
async def test_returns_none_on_phase_exhaustion(mock_client, semaphore):
    idx = MockIndex()
    incomplete_json = json.dumps({"focus_type": {"value": "X", "evidence": "e", "page": 1, "confidence": 80}})

    responses = [_make_response(_make_json_message(_metadata_json()))]
    for _ in range(10):
        responses.append(_make_response(_make_json_message(incomplete_json)))

    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is None


@pytest.mark.asyncio
async def test_verify_quote_tool_execution(mock_client, semaphore):
    idx = MockIndex()

    responses = [
        _make_response(_make_json_message(_metadata_json())),
        _make_response(_make_tool_call_message([
            {"id": "call_1", "name": "verify_quote", "args": '{"quote": "evaluation framework", "page_num": 1}'},
        ])),
        _make_response(_make_json_message(_phase1_json())),
    ]
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    # verify_quote was called, so there should be 3 API calls total
    assert mock_client.chat.completions.create.call_count == 3
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_agent_loop.py -v`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 4: Write `agent_loop.py`**

```python
"""Core agentic loop for the multi-phase extraction pipeline."""

import asyncio
import json
import logging

from openai import AsyncOpenAI

from schemas import PHASES, METADATA_FIELDS
from pdf_index import PDFIndex
from tools import TOOL_DEFINITIONS, execute_tool
from prompts import build_system_prompt, build_phase_user_message

MAX_TURNS_PER_PHASE = 10
MAX_PHASE_RETRIES = 3

logger = logging.getLogger(__name__)


def _parse_phase_response(phase_idx: int, content: str) -> dict | None:
    """Parse JSON response for a phase. Returns None on parse failure."""
    try:
        text = content.strip()
        if text.startswith("```"):
            import re
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _validate_phase_fields(phase_idx: int, data: dict) -> list[str]:
    """Return list of missing fields for this phase."""
    phase = PHASES[phase_idx]
    missing = []
    for field in phase["fields"]:
        if field not in data:
            missing.append(field)
    return missing


async def agent_loop(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
) -> dict | None:
    """Run 6-phase extraction with tool-use agent loop."""
    all_extracted: dict = {}
    messages: list[dict] = [{"role": "system", "content": build_system_prompt()}]
    full_text = index.get_full_text()

    for phase_idx, phase in enumerate(PHASES):
        phase_result = await _run_phase(
            client, model, semaphore, paper_id, index,
            phase_idx, messages, full_text, all_extracted,
        )
        if phase_result is None:
            logger.error("[%s] Phase %d/%d (%s) FAILED after all retries",
                         paper_id, phase_idx, len(PHASES) - 1, phase["name"])
            return None
        all_extracted.update(phase_result)
        logger.info("[%s] Phase %d/%d (%s) complete: %d fields",
                    paper_id, phase_idx, len(PHASES) - 1, phase["name"],
                    len(phase_result))

    return all_extracted


async def _run_phase(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
    phase_idx: int,
    messages: list[dict],
    full_text: str,
    extracted_so_far: dict,
) -> dict | None:
    for retry in range(MAX_PHASE_RETRIES):
        result = await _attempt_phase(
            client, model, semaphore, paper_id, index,
            phase_idx, messages, full_text, extracted_so_far,
        )
        if result is not None:
            return result
        if retry < MAX_PHASE_RETRIES - 1:
            logger.warning("[%s] Phase %d retry %d/%d",
                           paper_id, phase_idx, retry + 1, MAX_PHASE_RETRIES - 1)
            # Remove messages added during this failed attempt
            # We keep messages up to the system prompt + previous phase results
            while len(messages) > 1:
                messages.pop()
    return None


async def _attempt_phase(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
    phase_idx: int,
    messages: list[dict],
    full_text: str,
    extracted_so_far: dict,
) -> dict | None:
    user_msg = build_phase_user_message(phase_idx, full_text, extracted_so_far)
    messages.append({"role": "user", "content": user_msg})
    turn = 0
    tool_call_count = 0

    while turn < MAX_TURNS_PER_PHASE:
        turn += 1
        async with semaphore:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0,
            )

        choice = response.choices[0]
        assistant_msg = choice.message

        if assistant_msg.tool_calls:
            messages.append(assistant_msg.model_dump())
            for tc in assistant_msg.tool_calls:
                args = json.loads(tc.function.arguments)
                tool_result = execute_tool(index, tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })
                tool_call_count += 1
                logger.debug("[%s] Phase %d turn %d: %s(%s)",
                             paper_id, phase_idx, turn, tc.function.name, args)
            continue

        # No tool calls — LLM returned text (should be JSON)
        if assistant_msg.content is None:
            messages.append({"role": "assistant", "content": ""})
            messages.append({"role": "user", "content": "Error: empty response. Please return JSON with all fields."})
            continue

        messages.append({"role": "assistant", "content": assistant_msg.content})
        parsed = _parse_phase_response(phase_idx, assistant_msg.content)

        if parsed is None:
            messages.append({"role": "user", "content": "Error: invalid JSON. Please return valid JSON."})
            continue

        missing = _validate_phase_fields(phase_idx, parsed)
        if missing:
            messages.append({
                "role": "user",
                "content": f"Error: missing fields: {', '.join(missing)}. Please return JSON with ALL fields for this phase.",
            })
            continue

        logger.info("[%s] Phase %d done: %d turns, %d tool calls",
                    paper_id, phase_idx, turn, tool_call_count)
        return parsed

    return None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_agent_loop.py -v`
Expected: All 5 tests PASS

- [ ] **Step 6: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/agent_loop.py extract/test_agent_loop.py extract/pyproject.toml extract/uv.lock
git commit -m "feat: add agentic loop with tool dispatch and phase management"
```

---

## Task 6: Rewrite `evaluate.py`

Replace `call_llm` with `agent_loop`, import from new modules, add `--paper`, `--log-level`, `--force` CLI args.

**Files:**
- Modify: `extract/evaluate.py`
- Modify: `extract/test_evaluate.py`

- [ ] **Step 1: Rewrite `evaluate.py`**

Keep: `parse_llm_response`, `strip_code_fences`, `_clamp_confidence`, `_parse_structured_field`, `build_csv_row`, `generate_markdown`, `_append_field`, `load_existing_ids`, `parse_id`.

Remove: `call_llm`, `extract_text_with_pages`, `SYSTEM_PROMPT`, all constants (now in schemas.py), `MAX_RETRIES`.

Add: imports from new modules, new `main()` with `--paper`/`--log-level`/`--force`.

```python
"""
从 PDF 论文中提取评价方法论信息，使用 6 阶段 agentic pipeline。
输出与 theme_track.csv schema 完全对齐的 CSV 和验证 Markdown。

使用方式:
  1. 确保 .env 中已配置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
  2. uv run evaluate.py                        # 处理 paper/ 目录下所有新 PDF
  3. uv run evaluate.py --paper 1              # 仅处理 paper 1
  4. uv run evaluate.py --force                # 强制重新处理已有论文
  5. uv run evaluate.py --log-level DEBUG      # 详细日志
  6. 输出: eval_results.csv + eval_reports/*.md
"""

import argparse
import asyncio
import csv
import json
import logging
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from schemas import (
    CSV_COLUMNS, CSV_HEADER, INTERNAL_TO_CSV,
    METADATA_FIELDS, BOOL_FIELDS, SINGLE_CHOICE_FIELDS,
    FREE_TEXT_FIELDS, STRUCTURED_FIELDS,
)
from pdf_index import PDFIndex
from agent_loop import agent_loop

load_dotenv()

MAX_CONCURRENCY = 3
OUTPUT_CSV = Path(__file__).parent / "eval_results.csv"
REPORTS_DIR = Path(__file__).parent / "eval_reports"


# --- Response Parsing (unchanged) ---

def strip_code_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```\w*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


def _clamp_confidence(val) -> int:
    try:
        n = int(val)
    except (TypeError, ValueError):
        return 50
    return max(0, min(100, n))


def _parse_structured_field(data: dict, field: str) -> dict:
    field_data = data.get(field, {})
    return {
        "value": str(field_data.get("value", "")),
        "evidence": str(field_data.get("evidence", "")),
        "page": field_data.get("page"),
        "confidence": _clamp_confidence(field_data.get("confidence", 50)),
    }


def parse_llm_response(content: str) -> dict:
    """Parse JSON response from the agentic pipeline into structured dict.
    
    The agent returns all fields across all phases merged into one JSON object.
    Metadata fields are plain values; structured fields have value/evidence/page/confidence.
    """
    content = strip_code_fences(content)
    data = json.loads(content)

    result = {}
    result["title"] = str(data.get("title", ""))
    result["year"] = data.get("year", "")
    result["venue"] = str(data.get("venue", ""))
    result["domain"] = str(data.get("domain", ""))

    for field in BOOL_FIELDS:
        parsed = _parse_structured_field(data, field)
        value = parsed["value"].upper()
        parsed["value"] = value if value in ("YES", "NO") else "NO"
        result[field] = parsed

    for field, valid_options in SINGLE_CHOICE_FIELDS.items():
        parsed = _parse_structured_field(data, field)
        value = parsed["value"]
        parsed["value"] = value if value in valid_options else valid_options[-1]
        result[field] = parsed

    for field in FREE_TEXT_FIELDS:
        result[field] = _parse_structured_field(data, field)

    return result


# --- CSV Output (unchanged) ---

def build_csv_row(paper_id: str, parsed: dict) -> dict:
    row = {"Paper_ID": paper_id}
    row["Title"] = parsed.get("title", "")
    row["Year"] = parsed.get("year", "")
    row["Venue"] = parsed.get("venue", "")
    row["Domain"] = parsed.get("domain", "")
    for field in STRUCTURED_FIELDS:
        csv_name = INTERNAL_TO_CSV[field]
        row[csv_name] = parsed[field]["value"]
    return row


# --- Markdown Report (unchanged) ---

def generate_markdown(paper_id: str, parsed: dict) -> str:
    title = parsed.get("title", f"Paper {paper_id}")
    lines = [f"# Paper {paper_id}: {title}\n"]

    lines.append("## 基础元数据\n")
    lines.append(f"- **Year**: {parsed['year']}")
    lines.append(f"- **Venue**: {parsed['venue']}")
    lines.append(f"- **Domain**: {parsed['domain']}\n")

    lines.append("## 模拟/角色建模\n")
    for field in ["focus_type", "simulation_target", "persona_model_depth",
                   "uses_dynamic_state", "temporal_modeling_details"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估方法\n")
    for field in ["eval_human_experts", "eval_lay_users", "eval_user_study",
                   "eval_llm_judge", "eval_automatic"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估核心维度\n")
    for field in ["dim_realism", "dim_consistency", "dim_fidelity",
                   "dim_utility", "dim_human_learning",
                   "dim_emotional_plausibility", "dim_safety"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估深度\n")
    for field in ["raw_eval_metrics", "theory_operationalized", "behavior_eval_depth"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 干预敏感性\n")
    _append_field(lines, "intervention_sensitivity", parsed["intervention_sensitivity"])

    lines.append("## 交互/披露/理论\n")
    for field in ["interaction_level", "prompt_disclosure", "theory_grounding", "clinical_theory"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 信度与方法论\n")
    for field in ["reliability_reported", "agreement_method", "coding_options"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估质量标记\n")
    for field in ["has_rubric", "llm_judge_validated", "uses_standard_metrics",
                   "metric_interpretable", "comparable_to_prior_work",
                   "has_longitudinal_eval", "has_robustness_testing",
                   "has_failure_analysis", "sim_behavior_realistic", "dataset_available"]:
        _append_field(lines, field, parsed[field])

    return "\n".join(lines)


def _append_field(lines: list, field_name: str, field_data: dict):
    value = field_data["value"]
    confidence = field_data["confidence"]
    evidence = field_data["evidence"]
    page = field_data["page"]
    page_str = f"p.{page}" if page is not None else "N/A"
    lines.append(f"### {field_name}: {value} (confidence: {confidence})")
    lines.append(f"**Evidence** ({page_str}): {evidence}\n")


# --- Idempotency (unchanged) ---

def load_existing_ids(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["Paper_ID"] for row in reader if row.get("Paper_ID")}


def parse_id(filename: str) -> str:
    match = re.match(r"(\d+)", filename)
    return match.group(1) if match else filename


# --- Main ---

async def main():
    parser = argparse.ArgumentParser(description="从论文PDF提取评价方法论信息（agentic pipeline）")
    parser.add_argument("--dir", type=str, default=None, help="PDF目录路径（默认: paper/）")
    parser.add_argument("--paper", type=str, default=None, help="仅处理指定论文ID")
    parser.add_argument("--force", action="store_true", help="强制重新处理已有论文")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO"],
                        help="日志级别（默认: INFO）")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(message)s",
    )

    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    if not base_url or not api_key or not model:
        print("错误: 请在 .env 中设置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL")
        sys.exit(1)

    paper_dir = Path(args.dir) if args.dir else Path(__file__).parent / "paper"
    if not paper_dir.exists():
        print(f"错误: 目录不存在: {paper_dir}")
        sys.exit(1)

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    existing_ids = load_existing_ids(OUTPUT_CSV) if not args.force else set()

    if args.paper:
        pdf_path = paper_dir / f"{args.paper}.pdf"
        if not pdf_path.exists():
            print(f"错误: 文件不存在: {pdf_path}")
            sys.exit(1)
        pdfs = [pdf_path]
    else:
        pdfs = sorted(paper_dir.glob("*.pdf"), key=lambda p: parse_id(p.name))
        if not pdfs:
            print(f"在 {paper_dir} 中未找到 PDF 文件")
            sys.exit(1)
        if not args.force:
            pdfs = [p for p in pdfs if parse_id(p.name) not in existing_ids]

    if not pdfs:
        print("没有新增论文，全部已处理。")
        return

    REPORTS_DIR.mkdir(exist_ok=True)

    print(f"共 {len(pdfs)} 篇待处理（并发数 {MAX_CONCURRENCY}）...\n")

    tasks = []
    for pdf in pdfs:
        pid = parse_id(pdf.name)
        tasks.append(_process_paper(client, model, semaphore, pid, pdf))

    results = await asyncio.gather(*tasks)

    new_rows = []
    for pdf, parsed in zip(pdfs, results):
        if parsed is None:
            pid = parse_id(pdf.name)
            print(f"[{pid}] FAILED — skipped")
            continue
        pid = parse_id(pdf.name)
        new_rows.append(build_csv_row(pid, parsed))
        md_path = REPORTS_DIR / f"{pid}.md"
        md_path.write_text(generate_markdown(pid, parsed), encoding="utf-8")

    if new_rows:
        write_header = not OUTPUT_CSV.exists() or OUTPUT_CSV.stat().st_size == 0
        with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            if write_header:
                writer.writeheader()
            writer.writerows(new_rows)

    success = len(new_rows)
    failed = len(pdfs) - success
    print(f"\n完成！{success}/{len(pdfs)} 篇成功" + (f"，{failed} 篇失败" if failed else ""))
    print(f"验证文档已生成到 {REPORTS_DIR}/")


async def _process_paper(
    client: AsyncOpenAI, model: str, semaphore: asyncio.Semaphore,
    paper_id: str, pdf_path: Path,
) -> dict | None:
    logger = logging.getLogger(__name__)
    print(f"[{paper_id}] 开始处理: {pdf_path.name} ", end="", flush=True)
    try:
        index = PDFIndex(pdf_path)
    except Exception as e:
        print(f"PDF读取失败: {e}")
        return None

    print(f"({index.page_count} pages)")
    try:
        all_extracted = await agent_loop(client, model, semaphore, paper_id, index)
    except Exception as e:
        logger.error("[%s] agent_loop 异常: %s", paper_id, e)
        return None

    if all_extracted is None:
        return None

    # Convert merged JSON to the parsed format expected by build_csv_row / generate_markdown
    try:
        parsed = _convert_agent_output(all_extracted)
        print(f"[{paper_id}] OK")
        return parsed
    except Exception as e:
        logger.error("[%s] 输出解析失败: %s", paper_id, e)
        return None


def _convert_agent_output(data: dict) -> dict:
    """Convert raw agent loop output (merged phase JSONs) to parse_llm_response format."""
    result = {}
    result["title"] = str(data.get("title", ""))
    result["year"] = data.get("year", "")
    result["venue"] = str(data.get("venue", ""))
    result["domain"] = str(data.get("domain", ""))

    for field in BOOL_FIELDS:
        parsed = _parse_structured_field(data, field)
        value = parsed["value"].upper()
        parsed["value"] = value if value in ("YES", "NO") else "NO"
        result[field] = parsed

    for field, valid_options in SINGLE_CHOICE_FIELDS.items():
        parsed = _parse_structured_field(data, field)
        value = parsed["value"]
        parsed["value"] = value if value in valid_options else valid_options[-1]
        result[field] = parsed

    for field in FREE_TEXT_FIELDS:
        result[field] = _parse_structured_field(data, field)

    return result


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Update `test_evaluate.py`**

Remove stale `defects`/`theoretical_grounding`/`inter_rater_reliability` references. Keep all existing test structure.

```python
import json
import pytest
from evaluate import parse_llm_response, build_csv_row, generate_markdown


def _make_field(value, evidence="test evidence", page=1, confidence=80):
    return {"value": value, "evidence": evidence, "page": page, "confidence": confidence}


def _make_full_response(**overrides):
    base = {
        "title": "Test Paper",
        "eval_human_experts": _make_field("YES"),
        "eval_lay_users": _make_field("NO"),
        "eval_user_study": _make_field("YES"),
        "eval_llm_judge": _make_field("NO"),
        "eval_automatic": _make_field("YES"),
        "dim_realism": _make_field("NO"),
        "dim_consistency": _make_field("YES"),
        "dim_fidelity": _make_field("NO"),
        "dim_utility": _make_field("YES"),
        "dim_human_learning": _make_field("NO"),
        "dim_emotional_plausibility": _make_field("YES"),
        "dim_safety": _make_field("NO"),
        "interaction_level": _make_field("Extended"),
        "prompt_disclosure": _make_field("Partial"),
        "theory_grounding": _make_field("Weak"),
        "reliability_reported": _make_field("No"),
        "coding_options": _make_field("No"),
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_valid_response():
    raw = _make_full_response()
    result = parse_llm_response(raw)
    assert result["title"] == "Test Paper"
    assert result["eval_human_experts"]["value"] == "YES"
    assert result["eval_lay_users"]["value"] == "NO"
    assert result["interaction_level"]["value"] == "Extended"


def test_parse_strips_code_fences():
    raw_json = _make_full_response()
    raw = f"```json\n{raw_json}\n```"
    result = parse_llm_response(raw)
    assert result["title"] == "Test Paper"


def test_parse_clamps_confidence():
    raw = _make_full_response(eval_human_experts=_make_field("YES", confidence=150))
    result = parse_llm_response(raw)
    assert result["eval_human_experts"]["confidence"] == 100


def test_parse_invalid_bool_defaults_to_no():
    raw = _make_full_response(eval_human_experts=_make_field("MAYBE"))
    result = parse_llm_response(raw)
    assert result["eval_human_experts"]["value"] == "NO"


def test_parse_invalid_single_choice_uses_last_default():
    raw = _make_full_response(interaction_level=_make_field("Invalid"))
    result = parse_llm_response(raw)
    assert result["interaction_level"]["value"] == "Longitudinal"


def test_build_csv_row():
    parsed = parse_llm_response(_make_full_response())
    row = build_csv_row("28", parsed)
    assert row["Paper_ID"] == "28"
    assert row["eval_human_experts"] == "YES"
    assert row["eval_lay_users"] == "NO"
    assert row["interaction_level"] == "Extended"


def test_generate_markdown_contains_title():
    parsed = parse_llm_response(_make_full_response())
    md = generate_markdown("28", parsed)
    assert "Test Paper" in md
    assert "eval_human_experts" in md
    assert "confidence" in md
    assert "Evidence" in md


def test_generate_markdown_shows_page():
    parsed = parse_llm_response(_make_full_response())
    md = generate_markdown("28", parsed)
    assert "p.1" in md
```

- [ ] **Step 3: Run all tests**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest test_evaluate.py test_schemas.py -v`
Expected: All tests PASS

- [ ] **Step 4: Run full test suite**

Run: `cd /home/handy/Projects/LLM-Evaluate/extract && uv run pytest -v`
Expected: All tests across all test files PASS

- [ ] **Step 5: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/evaluate.py extract/test_evaluate.py
git commit -m "feat: rewrite evaluate.py to use agentic pipeline with 6-phase extraction"
```

---

## Task 7: Integration Verification

Run the full pipeline against `paper/1.pdf` and verify output format compatibility.

- [ ] **Step 1: Run pipeline against paper 1**

```bash
cd /home/handy/Projects/LLM-Evaluate/extract
uv run evaluate.py --paper 1 --force --log-level DEBUG
```

Expected: Pipeline completes successfully, new `eval_reports/1.md` generated.

- [ ] **Step 2: Verify CSV format**

```bash
cd /home/handy/Projects/LLM-Evaluate/extract
head -1 eval_results.csv
```

Expected: CSV header matches CSV_HEADER from schemas.py (44 columns).

- [ ] **Step 3: Verify markdown format**

```bash
cd /home/handy/Projects/LLM-Evaluate/extract
head -30 eval_reports/1.md
```

Expected: Markdown has same section structure as before (基础元数据, 模拟/角色建模, etc.).

- [ ] **Step 4: Commit**

```bash
cd /home/handy/Projects/LLM-Evaluate
git add extract/eval_results.csv extract/eval_reports/1.md
git commit -m "test: update eval results from agentic pipeline run"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] 6-phase extraction pipeline (Task 5 agent_loop)
- [x] 3 tools: search_text, read_page, verify_quote (Task 3)
- [x] PDFIndex with search/get_page (Task 2)
- [x] Fixed system prompt for caching (Task 4)
- [x] Per-phase user messages with extracted_so_far (Task 4)
- [x] Max 10 turns per phase, 3 retries (Task 5)
- [x] No default value filling — FAILED on exhaustion (Task 5)
- [x] --paper, --log-level, --force CLI args (Task 6)
- [x] Paper-level parallelism, phase-level serialization (Task 6)
- [x] Backward-compatible CSV/MD output (Task 6)
- [x] Logging at INFO and DEBUG levels (Task 5 + Task 6)
- [x] All existing functions preserved (parse_llm_response, build_csv_row, etc.)

**Placeholder scan:**
- [x] No TBD/TODO/Fill-in-later
- [x] No "similar to Task N" references
- [x] All code blocks contain actual code
- [x] All function/type names are consistent across tasks

**Type consistency:**
- [x] `PDFIndex` used consistently (Tasks 2, 3, 5, 6)
- [x] `execute_tool(index, tool_name, args)` signature consistent (Tasks 3, 5)
- [x] `agent_loop(client, model, semaphore, paper_id, index)` signature consistent (Tasks 5, 6)
- [x] `build_phase_user_message(phase_idx, full_text, extracted_so_far)` consistent (Tasks 4, 5)
