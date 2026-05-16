"""
verify_extraction.py - 验证 evaluate.py 提取结果的质量

用法:
  uv run .claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1
  uv run .claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1 28 35
  uv run .claude/skills/verify-eval-extraction/scripts/verify_extraction.py --all
"""

import json
import re
import sys
from pathlib import Path

# When run via `cd extract && uv run ../.claude/.../verify_extraction.py`,
# the script lives in .claude/skills/ but needs to find extract/ relative to project root.
# Resolve by walking up from the script until we find a directory containing extract/
def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "extract").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("Cannot find project root (directory containing extract/)")

PROJECT_ROOT = _find_project_root()
EXTRACT_DIR = PROJECT_ROOT / "extract"
REPORTS_DIR = EXTRACT_DIR / "eval_reports"
PAPER_DIR = EXTRACT_DIR / "paper"

# 复用 pdf_index.py 的归一化逻辑，保持验证结果与 pipeline 一致
sys.path.insert(0, str(EXTRACT_DIR))
from pdf_index import _normalize_whitespace as normalize, _clean_footnote_breaks

# 字段 → 搜索关键词映射，用于 --extract-evidence 从 PDF 提取候选证据
FIELD_KEYWORDS = {
    "eval_human_experts": ["professional", "expert", "clinician", "therapist", "psychologist", "psychiatrist", "annotator", "rater"],
    "eval_lay_users": ["volunteer", "participant", "mturk", "prolific", "crowd", "recruit", "user study"],
    "eval_user_study": ["interact", "session", "participant", "dialogue", "conversation", "task", "protocol"],
    "eval_llm_judge": ["gpt", "claude", "llm", "language model", "automatic", "score", "judge", "evaluat"],
    "eval_automatic": ["bleu", "rouge", "bertscore", "meteor", "f1", "accuracy", "precision", "recall", "metric"],
    "dim_realism": ["realism", "realistic", "natural", "human-like", "authentic", "plausible"],
    "dim_consistency": ["consist", "coherent", "stable", "maintain"],
    "dim_fidelity": ["fidelity", "accurate", "faithful", "adhere", "comply", "structure"],
    "dim_utility": ["useful", "helpful", "effective", "applicab", "beneficial", "practical"],
    "dim_human_learning": ["learn", "skill", "improve", "progress", "outcome", "training", "educat"],
    "dim_emotional_plausibility": ["emotion", "empathy", "affect", "sentiment", "mood", "feeling"],
    "dim_safety": ["safety", "harm", "toxic", "risk", "suicid", "crisis", "confidential"],
    "has_rubric": ["rubric", "scale", "criteria", "scoring", "rating", "likert", "criterion"],
    "reliability_reported": ["kappa", "alpha", "icc", "inter-rater", "inter-annotator", "agreement", "cohen", "fleiss"],
    "coding_options": ["inter-rater", "inter-annotator", "agreement", "cohen", "kappa", "iaa"],
    "theory_grounding": ["theory", "validated", "psychometric", "cbt", "clinical", "established", "framework"],
    "theory_operationalized": ["operationaliz", "measure", "assess", "metric", "scale", "instrument"],
    "interaction_level": ["turn", "round", "dialogue", "session", "multi-turn", "single-turn", "longitudinal"],
    "prompt_disclosure": ["prompt", "template", "appendix", "supplementary", "instruction"],
    "llm_judge_validated": ["correlat", "agreement", "pearson", "spearman", "validated", "human judgment"],
    "uses_standard_metrics": ["bleu", "rouge", "bertscore", "meteor", "standard", "established"],
    "metric_interpretable": ["interpret", "explain", "meaning", "coherence", "dimension"],
    "comparable_to_prior_work": ["baseline", "compar", "prior", "previous", "state-of-the-art", "sota"],
    "has_longitudinal_eval": ["longitudinal", "follow-up", "multiple session", "long-term", "over time"],
    "has_robustness_testing": ["robust", "adversar", "ablation", "sensitivity", "vary"],
    "has_failure_analysis": ["failure", "error", "limitation", "weakness", "flag", "incorrect"],
    "sim_behavior_realistic": ["realistic", "authentic", "simulation", "behavior", "real"],
    "dataset_available": ["available", "release", "public", "github", "hugging", "code", "data"],
    "clinical_theory": ["cbt", "dbt", "cognitive", "behavioral", "therapy", "clinical", "psychodynamic"],
    "focus_type": ["framework", "evaluation", "benchmark", "dataset", "model", "system"],
    "simulation_target": ["simulate", "agent", "patient", "therapist", "client", "persona"],
    "persona_model_depth": ["persona", "character", "profile", "trait", "dynamic", "static"],
    "uses_dynamic_state": ["dynamic", "state", "memory", "context", "temporal", "history"],
    "behavior_eval_depth": ["behavior", "dynamic", "pattern", "static", "change", "evolv"],
    "intervention_sensitivity": ["ablation", "intervention", "sensitivity", "component", "removal"],
    "raw_eval_metrics": ["metric", "score", "measure", "evaluation", "rating"],
    "temporal_modeling_details": ["temporal", "dynamic", "state", "memory", "iteration", "round"],
    "agreement_method": ["kappa", "alpha", "icc", "cohen", "fleiss", "agreement"],
}


def extract_pdf_pages(pdf_path: Path) -> dict[int, str]:
    """Extract PDF text per page, return {page_number: text}."""
    import fitz

    doc = fitz.open(str(pdf_path))
    pages = {}
    for i, page in enumerate(doc):
        pages[i + 1] = page.get_text()
    doc.close()
    return pages


def parse_report(md_path: Path) -> list[dict]:
    """Parse eval report Markdown into structured fields."""
    text = md_path.read_text(encoding="utf-8")
    # Extract title
    title_match = re.match(r"# Paper \d+: (.+)", text)
    title = title_match.group(1) if title_match else ""

    # Parse fields: ### field_name: value (confidence: N)\n**Evidence** (p.X): text
    pattern = (
        r"### (\w+): (.+?) \(confidence: \d+\)\n"
        r"\*\*Evidence\*\* \((.+?)\): (.+?)(?:\n|$)"
    )
    fields = []
    for field, value, page_str, evidence in re.findall(pattern, text):
        page = None
        if page_str != "N/A":
            try:
                page = int(page_str.replace("p.", ""))
            except ValueError:
                pass

        fields.append(
            {
                "field": field,
                "value": value.strip(),
                "page": page,
                "evidence": evidence.strip(),
            }
        )

    return {"title": title, "fields": fields}


def verify_evidence(
    evidence: str, norm_full: str, pages: dict[int, str], claimed_page: int | None
) -> dict:
    """Verify a single evidence claim. Returns verification result."""
    is_template = (
        evidence.startswith("No evidence of")
        or evidence.startswith("论文中未")
        or evidence.startswith("未发现")
        or evidence.startswith("未涉及")
    )

    if is_template:
        return {"quality": "TEMPLATE", "page_match": None, "detail": "Template text — needs real evidence from PDF"}

    # Handle ellipsis: split on "..." and verify each part independently
    parts = [p.strip() for p in evidence.split("...") if p.strip()]
    all_exact = True
    details = []
    page_found_on = None

    for part in parts:
        part_norm = normalize(part)
        if part_norm in norm_full:
            details.append(f'exact: "{_truncate(part, 40)}"')
        else:
            all_exact = False
            # Find longest matching substring
            matched = _find_longest_partial(part_norm, norm_full)
            if matched:
                details.append(f'partial: "{_truncate(part, 30)}" → matched "{_truncate(matched, 40)}"')
            else:
                details.append(f'NOT FOUND: "{_truncate(part, 50)}"')

    # Page verification
    page_match = None
    if claimed_page is not None and all_exact:
        # Check if evidence appears on the claimed page
        if claimed_page in pages:
            page_text = normalize(_clean_footnote_breaks(pages[claimed_page]))
            first_part_norm = normalize(parts[0]) if parts else ""
            if first_part_norm and first_part_norm in page_text:
                page_match = True
                page_found_on = claimed_page
            else:
                # Search all pages for the actual location
                for pn, pt in pages.items():
                    if first_part_norm in normalize(_clean_footnote_breaks(pt)):
                        page_found_on = pn
                        break
                page_match = page_found_on == claimed_page
        else:
            page_match = False

    if all_exact:
        quality = "EXACT"
    elif all(d == d for d in details) and any("partial:" in d for d in details):
        quality = "PARAPHRASED"
    else:
        quality = "FABRICATED"

    return {
        "quality": quality,
        "page_match": page_match,
        "page_found_on": page_found_on,
        "detail": "; ".join(details),
    }


def extract_judgment_hints(pages: dict[int, str]) -> dict:
    """Extract relevant snippets for judgment verification of tricky fields."""
    hints = {}
    # 预计算归一化后的页面文本，避免重复计算
    norm_pages = {pn: normalize(_clean_footnote_breaks(pt)) for pn, pt in pages.items()}

    def _search_keywords(keywords: list[str], max_hits: int = 3, extra_filter: list[str] | None = None) -> list[dict]:
        hits = []
        for kw in keywords:
            kw_norm = kw.replace("-", "").replace("'", "").replace("’", "")
            for pn, pt_norm in norm_pages.items():
                if kw_norm in pt_norm:
                    raw_pt = pages[pn]
                    sentences = re.split(r'[.!?\n]', raw_pt)
                    for s in sentences:
                        s_norm = normalize(s)
                        if kw_norm in s_norm:
                            if extra_filter and not any(f.replace("-","") in s_norm for f in extra_filter):
                                continue
                            hits.append({"page": pn, "text": s.strip()[:200]})
                            break
                    if len(hits) >= max_hits:
                        return hits
        return hits

    # reliability_reported / coding_options: look for standard coefficients
    reliability_keywords = [
        "cohen", "kappa", "krippendorff", "icc", "intra-class",
        "fleiss", "inter-rater", "inter-annotator agreement",
        "iaa", "annotator agreement",
    ]
    hits = _search_keywords(reliability_keywords)
    if hits:
        hints["reliability_reported"] = hits

    # eval_llm_judge: look for LLM scoring/evaluating
    judge_keywords = ["gpt-4", "gpt-3.5", "claude", "llm-as-judge", "llm as evaluator"]
    hits = _search_keywords(judge_keywords, extra_filter=["score", "evaluat", "rate", "judge", "assess"])
    if hits:
        hints["eval_llm_judge"] = hits

    # llm_judge_validated: look for correlation/agreement between LLM and human
    validated_keywords = [
        "correlation with human", "agreement with human",
        "human-llm agreement", "validated against",
        "pearson", "spearman",
    ]
    hits = _search_keywords(validated_keywords)
    if hits:
        hints["llm_judge_validated"] = hits

    # theory_grounding: look for validated scales/theories
    theory_keywords = [
        "validated", "validated instrument", "validated scale",
        "psychometric", "cbt", "cognitive-behavioral",
        "clinical trial", "established measure",
    ]
    hits = _search_keywords(theory_keywords)
    if hits:
        hints["theory_grounding"] = hits

    # prompt_disclosure: look for appendix/supplementary with prompts
    prompt_keywords = [
        "appendix", "supplementary", "prompt template",
        "full prompt", "prompt is provided",
    ]
    hits = _search_keywords(prompt_keywords)
    if hits:
        hints["prompt_disclosure"] = hits

    return hints


def _find_longest_partial(part_norm: str, norm_full: str) -> str | None:
    """Find the longest matching substring between evidence and PDF text."""
    words = part_norm.split()
    if len(words) < 3:
        return None
    for length in range(len(words), max(3, len(words) // 2), -1):
        for start in range(len(words) - length + 1):
            chunk = " ".join(words[start : start + length])
            if chunk in norm_full:
                return chunk
    return None


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def verify_paper(paper_id: str) -> dict | None:
    """Verify a single paper. Returns structured result."""
    report_path = REPORTS_DIR / f"{paper_id}.md"
    pdf_path = PAPER_DIR / f"{paper_id}.pdf"

    if not report_path.exists():
        return {"id": paper_id, "error": f"Report not found: {report_path}"}
    if not pdf_path.exists():
        return {"id": paper_id, "error": f"PDF not found: {pdf_path}"}

    report = parse_report(report_path)
    pages = extract_pdf_pages(pdf_path)
    norm_full = normalize(_clean_footnote_breaks("".join(pages.values())))

    results = []
    for field_data in report["fields"]:
        ver = verify_evidence(
            field_data["evidence"],
            norm_full,
            pages,
            field_data["page"],
        )
        results.append(
            {
                "field": field_data["field"],
                "value": field_data["value"],
                "claimed_page": field_data["page"],
                "quality": ver["quality"],
                "page_match": ver["page_match"],
                "page_found_on": ver.get("page_found_on"),
                "detail": ver["detail"],
            }
        )

    hints = extract_judgment_hints(pages)

    # Summary counts
    counts = {"EXACT": 0, "PARAPHRASED": 0, "FABRICATED": 0, "TEMPLATE": 0}
    for r in results:
        counts[r["quality"]] += 1

    return {
        "id": paper_id,
        "title": report["title"],
        "fields": results,
        "judgment_hints": hints,
        "summary": counts,
    }


def extract_evidence_candidates(pages: dict[int, str], field: str, value: str, evidence: str, top_n: int = 10) -> list[dict]:
    """从 PDF 中提取与字段相关的候选 verbatim 原文片段。"""
    keywords = FIELD_KEYWORDS.get(field, [])
    if not keywords:
        return []

    # 从 evidence 中提取额外关键词（去掉模板前缀）
    extra_kws = []
    if evidence.startswith("No evidence of") or evidence.startswith("论文中未") or evidence.startswith("未发现"):
        # TEMPLATE: 从 evidence 中提取有意义的词
        cleaned = re.sub(r'^(No evidence of |论文中未[^，]*，|未发现[^。]*。|未涉及[^。]*。)', '', evidence)
        extra_kws = [w for w in cleaned.split() if len(w) > 3][:5]
    else:
        # FABRICATED: 从 evidence 中提取名词短语
        words = evidence.split()
        extra_kws = [w for w in words if len(w) > 4 and w[0].isupper()][:5]

    all_keywords = keywords + extra_kws

    # 按句子分割 PDF 全文，计算每个句子的相关度
    candidates = []
    for pn, page_text in pages.items():
        # 按句号、感叹号、问号、换行分割
        sentences = re.split(r'(?<=[.!?])\s+|\n', page_text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 500:
                continue
            sentence_lower = sentence.lower()
            # 计算关键词命中数
            hits = sum(1 for kw in all_keywords if kw.lower() in sentence_lower)
            if hits >= 1:
                candidates.append({
                    "page": pn,
                    "text": sentence[:300],
                    "relevance": hits,
                })

    # 按相关度降序排序，去重，返回 top_n
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    seen = set()
    unique = []
    for c in candidates:
        key = c["text"][:80]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique[:top_n]


def compute_fixes(result: dict) -> list[dict]:
    """Compute needed fixes for a single paper's verification result."""
    fixes = []
    for field_data in result.get("fields", []):
        field = field_data["field"]
        quality = field_data["quality"]
        claimed_page = field_data["claimed_page"]
        page_found_on = field_data.get("page_found_on")
        value = field_data["value"]

        # Fix page number: evidence is EXACT but on wrong page
        if quality == "EXACT" and claimed_page is not None and page_found_on is not None and claimed_page != page_found_on:
            fixes.append({
                "field": field,
                "type": "page_fix",
                "old_page": claimed_page,
                "new_page": page_found_on,
                "description": f"p.{claimed_page} → p.{page_found_on}",
            })

        # Mark TEMPLATE and FABRICATED fields for PDF search (not template replacement)
        if quality in ("TEMPLATE", "FABRICATED"):
            fixes.append({
                "field": field,
                "type": "needs_pdf_search",
                "old_quality": quality,
                "value": value,
                "description": f"{quality} — need to search PDF for real evidence",
            })

    return fixes


def apply_fixes(paper_id: str, report_path: Path, fixes: list[dict]) -> None:
    """Apply fixes to a report file in-place. Only handles page fixes."""
    content = report_path.read_text(encoding="utf-8")
    for fix in fixes:
        if fix["type"] == "page_fix":
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if f"### {fix['field']}:" in line:
                    new_lines.append(line)
                elif f"**Evidence** (p.{fix['old_page']}):" in line:
                    line = line.replace(f"(p.{fix['old_page']})", f"(p.{fix['new_page']})")
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
    report_path.write_text(content, encoding="utf-8")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: verify_extraction.py <id> [<id> ...] | --all [--fix]")
        sys.exit(1)

    do_fix = "--fix" in args
    args = [a for a in args if a != "--fix"]

    if not args:
        print("Usage: verify_extraction.py <id> [<id> ...] | --all [--fix]")
        sys.exit(1)

    if args[0] == "--all":
        ids = sorted(
            p.stem for p in REPORTS_DIR.glob("*.md") if p.stem.isdigit()
        )
    else:
        ids = args

    all_results = []
    all_fixes = {}
    for paper_id in ids:
        result = verify_paper(paper_id)
        if result:
            all_results.append(result)
            if do_fix:
                report_path = REPORTS_DIR / f"{paper_id}.md"
                if report_path.exists() and "fields" in result:
                    fixes = compute_fixes(result)
                    if fixes:
                        apply_fixes(paper_id, report_path, fixes)
                        all_fixes[paper_id] = fixes

    output = {
        "papers": all_results,
        "batch_summary": {
            "total_papers": len(all_results),
            "total_fields": sum(
                sum(1 for _ in p.get("fields", [])) for p in all_results
            ),
            "quality_counts": {
                "EXACT": sum(p["summary"]["EXACT"] for p in all_results if "summary" in p),
                "PARAPHRASED": sum(
                    p["summary"]["PARAPHRASED"] for p in all_results if "summary" in p
                ),
                "FABRICATED": sum(
                    p["summary"]["FABRICATED"] for p in all_results if "summary" in p
                ),
                "TEMPLATE": sum(
                    p["summary"]["TEMPLATE"] for p in all_results if "summary" in p
                ),
            },
        },
    }

    if do_fix:
        output["fixes_applied"] = all_fixes

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
