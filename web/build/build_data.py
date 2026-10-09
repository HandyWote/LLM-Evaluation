#!/usr/bin/env python3
"""
Build the web data files for the codebook site.

Reads (never modifies) the authoritative source files:
  - docs/09_appendices.tex                     -> codebook definitions (7 groups / 40 fields)
  - compare/final-table.csv                    -> paper-level coding (G1-G6)
  - table/theory_eval_refined_coding_refined.csv -> theory fields (G5 override; matches the paper)
  - compare/claim_level_FINAL_analysis_ready.csv -> claim-evidence alignment (G7)

Outputs JSON into web/data/:
  codebook.json  groups[{id,name,description,fields[{name,values,type,definition}]}]
  papers.json    {n, fields:[...], papers:[{Paper_ID,Citation_Key,Title,Year,Venue,values:{...}}]}
  claims.json    {n_slots,n_papers,slots:[...],summary:{...}}
  stats.json     overview numbers, all computed from the CSVs

Usage:
    python3 web/build/build_data.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "data"

APPENDIX = ROOT / "docs" / "09_appendices.tex"
FINAL_TABLE = ROOT / "compare" / "final-table.csv"
THEORY_CSV = ROOT / "table" / "theory_eval_refined_coding_refined.csv"
CLAIM_CSV = ROOT / "compare" / "claim_level_FINAL_analysis_ready.csv"

# ---------------------------------------------------------------- codebook ----


def _clean(s: str) -> str:
    s = s.replace("\\\\_", "_").replace("\\_", "_")
    s = s.replace("\\textsc{", "").replace("\\texttt{", "")
    s = re.sub(r"\\ref\{[^}]*\}", "", s)
    s = s.replace("~", " ")
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_codebook() -> list[dict]:
    tex = APPENDIX.read_text(encoding="utf-8")
    seg = tex[tex.index("\\section{Coding Scheme}"):]
    # cut off the sections that follow the codebook subsections
    seg = seg.split("\\section{Coding Reliability}")[0]
    parts = re.split(r"\\subsection\{([^}]*)\}", seg)

    groups: list[dict] = []
    for i in range(1, len(parts), 2):
        name = parts[i].strip()
        body = parts[i + 1]
        # intro paragraph = text between the subsection header and the first table
        intro = body.split("\\begin{table")[0]
        intro = _clean(intro)
        fields = []
        for m in re.finditer(
            r"\\texttt\{([^}]+)\}\s*&\s*(.*?)\s*&\s*(.*?)\s*\\\\",
            body,
            re.DOTALL,
        ):
            fname = _clean(m.group(1))
            values = _clean(m.group(2))
            definition = _clean(m.group(3))
            if not fname or fname in {f["name"] for f in fields}:
                continue
            fields.append(
                {
                    "name": fname,
                    "values": values,
                    "type": _infer_type(values),
                    "definition": definition,
                }
            )
        groups.append({"id": f"G{len(groups) + 1}", "name": name, "description": intro, "fields": fields})
    return groups


def _infer_type(values: str) -> str:
    if values.strip().lower().startswith("yes / no"):
        return "boolean"
    if values.strip().lower() == "free text":
        return "text"
    if ";" in values or "multi-label" in values.lower():
        return "multi-label"
    if "/" in values:
        return "single-choice"
    return "other"


# ------------------------------------------------------------------- data -----


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def yes(r: dict, col: str) -> bool:
    return (r.get(col) or "").strip().lower() == "yes"


def build_papers(codebook: list[dict]) -> dict:
    rows = read_csv(FINAL_TABLE)
    theory = {r["Citation_Key"]: r for r in read_csv(THEORY_CSV)}

    # the 40 codebook field names (paper-level groups G1..G6 + G7 placeholders)
    field_names = [f["name"] for g in codebook for f in g["fields"]]
    g7 = {"Claim", "Claim_Evidence_Alignment"}

    # map codebook field name -> final-table column name
    col_map = {
        "Intervention_Sensitivity": "Interention_Sensitivity",  # typo in the CSV header
    }

    papers = []
    for r in rows:
        ck = r["Citation_Key"]
        values: dict[str, str] = {}
        for name in field_names:
            if name in g7:
                continue
            if name == "Theory_Grounding":
                values[name] = (theory.get(ck, {}).get("Theory_Grounding") or "").strip()
            elif name == "Theory_Operationalized":
                values[name] = (
                    theory.get(ck, {}).get("Theory_Operationalized_In_Evaluation") or ""
                ).strip()
            elif name == "Theory_Eval_Type":
                values[name] = (theory.get(ck, {}).get("Theory_Eval_Type") or "").strip()
            else:
                col = col_map.get(name, name)
                values[name] = (r.get(col) or "").strip()
        papers.append(
            {
                "Paper_ID": r["Paper_ID"],
                "Citation_Key": ck,
                "Title": (r.get("Title") or "").strip(),
                "Year": (r.get("Year") or "").strip(),
                "Venue": (r.get("Venue") or "").strip(),
                "values": values,
            }
        )
    papers.sort(key=lambda p: int(p["Paper_ID"]) if p["Paper_ID"].isdigit() else 999)
    return {"n": len(papers), "fields": [f for f in field_names if f not in g7], "papers": papers}


CLAIM_FIELDS = [
    "Paper_ID",
    "Citation_Key",
    "Title",
    "Claim_Slot",
    "Claim_Quote",
    "Claim_Page",
    "Claim_Section",
    "Evidence_Quote",
    "Evidence_Page",
    "Evidence_Section",
    "Evidence_Location_Detail",
    "Final_Alignment",
    "Final_Decision_Type",
    "Human_Review_Flag",
]


def build_claims() -> dict:
    rows = read_csv(CLAIM_CSV)
    slots = [{k: (r.get(k) or "").strip() for k in CLAIM_FIELDS} for r in rows]

    def dist(subset: list[dict]) -> dict:
        c = Counter(s["Final_Alignment"] for s in subset)
        return {k: c.get(k, 0) for k in ("ALIGNED", "PARTIAL", "EXCEEDS", "UNCLEAR")}

    c1 = [s for s in slots if s["Claim_Slot"] == "C1"]
    c2 = [s for s in slots if s["Claim_Slot"] == "C2"]
    summary = {
        "n_slots": len(slots),
        "n_papers": len({s["Citation_Key"] for s in slots}),
        "c1": {"n": len(c1), **dist(c1)},
        "c2": {"n": len(c2), **dist(c2)},
        "all": {"n": len(slots), **dist(slots)},
    }
    return {"n_slots": len(slots), "n_papers": summary["n_papers"], "slots": slots, "summary": summary}


THEORY_EVAL_TYPES = [
    "Validated scale",
    "Established therapy/counseling coding system",
    "Theory-specific rubric",
    "Custom expert rating",
    "Affective/emotional dynamics metric",
    "Clinical diagnostic benchmark",
    "Theory-specific benchmark/task",
    "LLM judge with theory-specific criteria",
]


def build_stats(codebook: list[dict]) -> dict:
    ft = read_csv(FINAL_TABLE)
    theory = read_csv(THEORY_CSV)
    n = len(ft)
    dims6 = ["Utility", "Fidelity", "Realism", "Emotional Plausibility", "Consistency", "Safety"]

    def cnt(col: str) -> int:
        return sum(1 for r in ft if yes(r, col))

    ext = [r for r in ft if (r.get("Interaction_Level") or "").strip() == "Extended Dialogue"]
    tcounts = Counter()
    for r in theory:
        for t in (r.get("Theory_Eval_Type") or "").split(";"):
            t = t.strip()
            if t:
                tcounts[t] += 1

    return {
        "n": n,
        "evaluators": [
            {"name": "Human experts", "n": cnt("Eval_Human_Experts")},
            {"name": "LLM judges", "n": cnt("Eval_LLM_Judge")},
            {"name": "Automatic metrics", "n": cnt("Eval_Automatic")},
            {
                "name": "All three",
                "n": sum(
                    1
                    for r in ft
                    if yes(r, "Eval_Human_Experts") and yes(r, "Eval_LLM_Judge") and yes(r, "Eval_Automatic")
                ),
            },
        ],
        "dimensions": [
            {"name": d, "n": cnt(d)}
            for d in [
                "Utility",
                "Fidelity",
                "Realism",
                "Emotional Plausibility",
                "Consistency",
                "Safety",
                "Human Learning / Outcomes",
            ]
        ],
        "funnel": [
            {"name": "All reviewed papers", "n": n},
            {"name": "Evaluate extended dialogues", "n": len(ext)},
            {"name": "Model dynamic user state", "n": cnt("Uses_Dynamic_State")},
            {"name": "Longitudinal evaluation", "n": cnt("Has_Longitudinal_Eval")},
        ],
        "behavior_depth_extended": dict(Counter((r.get("Behavior_Eval_Depth") or "").strip() for r in ext)),
        "rubric": {
            "has": cnt("Has_Rubric"),
            "reported_reliability": sum(
                1 for r in ft if yes(r, "Has_Rubric") and yes(r, "Reliability_Reported")
            ),
        },
        "llm_judge": {
            "used": cnt("Eval_LLM_Judge"),
            "validated": sum(1 for r in ft if yes(r, "Eval_LLM_Judge") and yes(r, "LLM_Judge_Validated")),
        },
        "prompt_disclosure": dict(Counter((r.get("Prompt_Disclosure") or "").strip() for r in ft)),
        "theory_grounding": dict(Counter((r.get("Theory_Grounding") or "").strip() for r in theory)),
        "theory_operationalized": dict(
            Counter((r.get("Theory_Operationalized_In_Evaluation") or "").strip() for r in theory)
        ),
        "theory_eval_types": {t: tcounts.get(t, 0) for t in THEORY_EVAL_TYPES},
        "dims_ge1": sum(1 for r in ft if sum(1 for d in dims6 if yes(r, d)) >= 1),
        "dims_ge3": sum(1 for r in ft if sum(1 for d in dims6 if yes(r, d)) >= 3),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    codebook = parse_codebook()
    papers = build_papers(codebook)
    claims = build_claims()
    stats = build_stats(codebook)

    (OUT / "codebook.json").write_text(json.dumps(codebook, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "papers.json").write_text(json.dumps(papers, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")

    # a single JS bundle so the page works from file:// (fetch() is blocked there)
    bundle = {"codebook": codebook, "papers": papers, "claims": claims, "stats": stats}
    (OUT / "data.js").write_text(
        "window.SURVEY_DATA = " + json.dumps(bundle, ensure_ascii=False) + ";\n", encoding="utf-8"
    )

    nfields = sum(len(g["fields"]) for g in codebook)
    print(f"codebook: {len(codebook)} groups, {nfields} fields")
    print(f"papers:   {papers['n']} papers x {len(papers['fields'])} fields")
    print(f"claims:   {claims['n_slots']} slots / {claims['n_papers']} papers")
    print(f"stats:    grounding={stats['theory_grounding']} op={stats['theory_operationalized']}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
