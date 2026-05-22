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
import traceback
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from lib.schemas import (
    CSV_COLUMNS, CSV_HEADER, INTERNAL_TO_CSV,
    METADATA_FIELDS, BOOL_FIELDS, SINGLE_CHOICE_FIELDS,
    FREE_TEXT_FIELDS, STRUCTURED_FIELDS,
)
from extract.pdf_index import PDFIndex
from extract.agent_loop import agent_loop

load_dotenv()

MAX_CONCURRENCY = 3
OUTPUT_CSV = Path(__file__).parent / "eval_results.csv"
PAPER_META_CSV = Path(__file__).parent.parent / "docs" / "paper_metadata.csv"
REPORTS_DIR = Path(__file__).parent.parent / "eval_reports"


# --- Response Parsing ---

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
    """Parse JSON response from the agentic pipeline into structured dict."""
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


# --- Bibtex Generation ---

def _load_paper_metadata() -> dict[str, dict]:
    if not PAPER_META_CSV.exists():
        return {}
    with open(PAPER_META_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        field_map = {k.strip(): k for k in (reader.fieldnames or [])}
        meta = {}
        for row in reader:
            pid = row.get(field_map.get("ID", ""), "").strip()
            if pid:
                meta[pid] = {
                    "first_author": row.get(field_map.get("First Author", ""), "").strip(),
                    "year": row.get(field_map.get("Year", ""), "").strip(),
                    "title": row.get(field_map.get("Title", ""), "").strip(),
                }
        return meta


def generate_bibtex_key(first_author: str, year: str, title: str) -> str:
    last_name = first_author.strip().split()[-1] if first_author.strip() else ""
    first_word_match = re.match(r"[A-Za-z]+", title)
    first_word = first_word_match.group(0) if first_word_match else ""
    return f"{last_name}{year}{first_word}"


_PAPER_META_CACHE: dict[str, dict] | None = None


def _get_paper_meta() -> dict[str, dict]:
    global _PAPER_META_CACHE
    if _PAPER_META_CACHE is None:
        _PAPER_META_CACHE = _load_paper_metadata()
    return _PAPER_META_CACHE


def _bibtex_for(paper_id: str) -> str:
    meta = _get_paper_meta().get(paper_id, {})
    return generate_bibtex_key(
        meta.get("first_author", ""),
        meta.get("year", ""),
        meta.get("title", ""),
    )


# --- CSV Output ---

def build_csv_row(paper_id: str, parsed: dict) -> dict:
    row = {"Paper_ID": paper_id}
    row["Citation_Key"] = _bibtex_for(paper_id)
    row["Bibtex"] = ""
    row["Title"] = parsed.get("title", "")
    row["Year"] = parsed.get("year", "")
    row["Venue"] = parsed.get("venue", "")
    row["Domain"] = parsed.get("domain", "")
    for field in STRUCTURED_FIELDS:
        csv_name = INTERNAL_TO_CSV[field]
        row[csv_name] = parsed[field]["value"]
    return row


# --- Markdown Report ---

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


# --- Idempotency ---

def load_existing_ids(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["Paper_ID"] for row in reader if row.get("Paper_ID")}


def backfill_bibtex():
    if not OUTPUT_CSV.exists():
        return
    with open(OUTPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        old_fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if "Citation_Key" in old_fieldnames:
        return

    new_fieldnames = [old_fieldnames[0], "Citation_Key", "Bibtex"] + old_fieldnames[1:]
    for row in rows:
        pid = row.get("Paper_ID", "")
        row["Citation_Key"] = _bibtex_for(pid)
        row["Bibtex"] = ""

    tmp = OUTPUT_CSV.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(OUTPUT_CSV)
    print(f"已回填 {len(rows)} 行的 Citation_Key 和 Bibtex 列")


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
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

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

    backfill_bibtex()

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
        logger.debug(traceback.format_exc())
        return None

    if all_extracted is None:
        return None

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
