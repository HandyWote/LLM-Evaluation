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


def extract_pdf_pages(pdf_path: Path) -> dict[int, str]:
    """Extract PDF text per page, return {page_number: text}."""
    import fitz

    doc = fitz.open(str(pdf_path))
    pages = {}
    for i, page in enumerate(doc):
        pages[i + 1] = page.get_text()
    doc.close()
    return pages


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower().strip()


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

        # Handle list values (defects)
        if ", " in value and field == "defects":
            pass  # keep as-is

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
        return {"quality": "TEMPLATE", "page_match": None, "detail": ""}

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
            page_text = normalize(pages[claimed_page])
            first_part_norm = normalize(parts[0]) if parts else ""
            if first_part_norm and first_part_norm in page_text:
                page_match = True
                page_found_on = claimed_page
            else:
                # Search all pages for the actual location
                for pn, pt in pages.items():
                    if first_part_norm in normalize(pt):
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
    full_text = "\n".join(pages.values()).lower()
    hints = {}

    # inter_rater_reliability: look for standard coefficients
    reliability_keywords = [
        "cohen", "kappa", "krippendorff", "icc", "intra-class",
        "fleiss", "inter-rater", "inter-annotator agreement",
        "iaa", "annotator agreement",
    ]
    reliability_hits = []
    for kw in reliability_keywords:
        for pn, pt in pages.items():
            if kw in pt.lower():
                # Extract sentence containing the keyword
                sentences = re.split(r'[.!?\n]', pt)
                for s in sentences:
                    if kw in s.lower():
                        reliability_hits.append({"page": pn, "text": s.strip()[:200]})
    if reliability_hits:
        hints["inter_rater_reliability"] = reliability_hits[:3]

    # eval_llm_judge: look for LLM scoring/evaluating
    judge_keywords = ["gpt-4", "gpt-3.5", "claude", "llm-as-judge", "llm as evaluator"]
    judge_hits = []
    for kw in judge_keywords:
        for pn, pt in pages.items():
            if kw in pt.lower():
                sentences = re.split(r'[.!?\n]', pt)
                for s in sentences:
                    if kw in s.lower() and any(
                        w in s.lower() for w in ["score", "evaluat", "rate", "judge", "assess"]
                    ):
                        judge_hits.append({"page": pn, "text": s.strip()[:200]})
    if judge_hits:
        hints["eval_llm_judge"] = judge_hits[:3]

    # theoretical_grounding: look for validated scales/theories
    theory_keywords = [
        "validated", "validated instrument", "validated scale",
        "psychometric", "cbt", "cognitive-behavioral",
        "clinical trial", "established measure",
    ]
    theory_hits = []
    for kw in theory_keywords:
        for pn, pt in pages.items():
            if kw in pt.lower():
                sentences = re.split(r'[.!?\n]', pt)
                for s in sentences:
                    if kw in s.lower():
                        theory_hits.append({"page": pn, "text": s.strip()[:200]})
    if theory_hits:
        hints["theoretical_grounding"] = theory_hits[:3]

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
    norm_full = normalize("".join(pages.values()))

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


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: verify_extraction.py <id> [<id> ...] | --all")
        sys.exit(1)

    if args[0] == "--all":
        ids = sorted(
            p.stem for p in REPORTS_DIR.glob("*.md") if p.stem.isdigit()
        )
    else:
        ids = args

    all_results = []
    for paper_id in ids:
        result = verify_paper(paper_id)
        if result:
            all_results.append(result)

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

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
