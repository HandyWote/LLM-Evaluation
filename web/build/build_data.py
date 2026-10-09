#!/usr/bin/env python3
"""
Build the web data files for the codebook site.

Reads (never modifies) the authoritative source files:
  - docs/09_appendices.tex                      -> codebook definitions (7 groups / 40 fields)
  - compare/final-table.csv                     -> paper-level coding (G1-G6) + Bibtex metadata
  - table/theory_eval_refined_coding_refined.csv -> theory fields (G5 override; matches the paper)
  - compare/claim_level_FINAL_analysis_ready.csv -> claim-evidence alignment (G7)

Outputs JSON into web/data/:
  codebook.json  {groups:[{id,name,description,fields:[{name,values,type,definition,gate?}]}], n_groups, n_fields}
  papers.json    {n, fields:[...], papers:[{Paper_ID,Citation_Key,Title,Year,Venue,values:{...}}]}
  claims.json    {n_slots,n_papers,slots:[... + Paper_URL,Claim_URL,Evidence_URL],summary:{...},
                  papers_with_url,papers_without_url,papers_without_url_ids}
  stats.json     overview numbers, gated statistics, behavioral validity, clinical theory
  data.js        all of the above as one window.SURVEY_DATA bundle

Also copies the four released source files byte-for-byte into web/downloads/ so the
Downloads section of the site serves the actual released files.

Usage:
    python3 web/build/build_data.py
"""

from __future__ import annotations

import csv
import itertools
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "data"
DOWNLOADS = Path(__file__).resolve().parents[1] / "downloads"

APPENDIX = ROOT / "docs" / "09_appendices.tex"
FINAL_TABLE = ROOT / "compare" / "final-table.csv"
THEORY_CSV = ROOT / "table" / "theory_eval_refined_coding_refined.csv"
CLAIM_CSV = ROOT / "compare" / "claim_level_FINAL_analysis_ready.csv"

# released files that are bundled (copied byte-for-byte) into web/downloads/
DOWNLOAD_FILES = [
    (FINAL_TABLE, "final-table.csv"),
    (THEORY_CSV, "theory_eval_refined_coding_refined.csv"),
    (CLAIM_CSV, "claim_level_FINAL_analysis_ready.csv"),
    (APPENDIX, "09_appendices.tex"),
]

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
    _attach_gates(groups)
    return groups


def _infer_type(values: str) -> str:
    v = values.strip()
    low = v.lower()
    if low == "free text":
        return "text"
    if low == "yes / no":
        return "boolean"
    # "Yes / No / N/A" is not a boolean: the third value makes the field unordered,
    # so it must be treated as a single-choice field (see FROZEN CONTRACT item 1).
    if low.startswith("yes / no"):
        return "single-choice"
    if ";" in v or "multi-label" in low:
        return "multi-label"
    if "/" in v:
        return "single-choice"
    return "other"


# Gate metadata: these two boolean fields are only interpretable for the papers
# where the gating question applies. Unconditional counts must carry the gate.
GATES = {
    "LLM_Judge_Validated": {
        "gate_field": "Eval_LLM_Judge",
        "gate_value": "Yes",
        "gate_note": (
            "Only interpretable for the 30 papers that use an LLM judge "
            "(Eval_LLM_Judge = Yes). A count over all 52 papers mixes in papers "
            "where the question does not apply and must never be shown without "
            "stating that denominator."
        ),
    },
    "Reliability_Reported": {
        "gate_field": "Has_Rubric",
        "gate_value": "Yes",
        "gate_note": (
            "Only interpretable for the 45 papers that provide a rubric or "
            "scoring criteria (Has_Rubric = Yes). A count over all 52 papers "
            "mixes in papers where the question does not apply and must never "
            "be shown without stating that denominator."
        ),
    },
}


def _attach_gates(groups: list[dict]) -> None:
    for g in groups:
        for f in g["fields"]:
            if f["name"] in GATES:
                f["gate"] = GATES[f["name"]]


# ------------------------------------------------------- value normalization --

# Type-aware canonicalization: boolean / single-choice values are matched
# case- and whitespace-insensitively against the codebook `values` string and
# rewritten in the codebook's canonical spelling (e.g. raw "NO" -> "No").
# The verbatim `values` string itself is never modified, and values that are not
# a case/whitespace variant of a listed option are kept exactly as reported
# (e.g. "N/A", or free-text clinical theory strings).
NORMALIZED_TYPES = {"boolean", "single-choice"}


def _canonical_index(values: str) -> dict[str, str]:
    index: dict[str, str] = {}
    for part in values.split("/"):
        part = re.sub(r"\s+", " ", part.strip())
        if part:
            index.setdefault(part.casefold(), part)
    return index


def _normalize_value(value: str, index: dict[str, str]) -> str:
    value = (value or "").strip()
    if not value:
        return value
    return index.get(re.sub(r"\s+", " ", value).casefold(), value)


# ------------------------------------------------------------------- data -----


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def yes(r: dict, col: str) -> bool:
    return (r.get(col) or "").strip().lower() == "yes"


def _strip(v: str) -> str:
    return (v or "").strip()


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

    # canonical spelling index for every boolean / single-choice codebook field
    normalizers = {
        f["name"]: _canonical_index(f["values"])
        for g in codebook
        for f in g["fields"]
        if f["type"] in NORMALIZED_TYPES
    }

    papers = []
    for r in rows:
        ck = r["Citation_Key"]
        values: dict[str, str] = {}
        for name in field_names:
            if name in g7:
                continue
            if name == "Theory_Grounding":
                val = _strip(theory.get(ck, {}).get("Theory_Grounding"))
            elif name == "Theory_Operationalized":
                val = _strip(theory.get(ck, {}).get("Theory_Operationalized_In_Evaluation"))
            elif name == "Theory_Eval_Type":
                val = _strip(theory.get(ck, {}).get("Theory_Eval_Type"))
            else:
                col = col_map.get(name, name)
                val = _strip(r.get(col))
            if name in normalizers:
                val = _normalize_value(val, normalizers[name])
            values[name] = val
        papers.append(
            {
                "Paper_ID": r["Paper_ID"],
                "Citation_Key": ck,
                "Title": _strip(r.get("Title")),
                "Year": _strip(r.get("Year")),
                "Venue": _strip(r.get("Venue")),
                "values": values,
            }
        )
    papers.sort(key=lambda p: int(p["Paper_ID"]) if p["Paper_ID"].isdigit() else 999)
    return {"n": len(papers), "fields": [f for f in field_names if f not in g7], "papers": papers}


# ---------------------------------------------------------------- claims ------


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


def _bib_field(bib: str, name: str) -> str:
    """Extract a BibTeX field value (only url/doi/eprint are used; these never contain nested braces)."""
    if not bib:
        return ""
    m = re.search(
        r"(?<![A-Za-z])" + re.escape(name) + r"\s*=\s*[\{\"](.*?)[\}\"]\s*,?",
        bib,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip().strip("{}").strip()


ARXIV_ID_RE = re.compile(r"(?:\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+(?:\.[A-Z]{2})?/\d{7})", re.IGNORECASE)


def _arxiv_id(value: str) -> str:
    """Return a valid arXiv id, or '' for placeholder / malformed eprint values."""
    value = _strip(value)
    return value if re.fullmatch(ARXIV_ID_RE, value) else ""


def _first_url(value: str) -> str:
    """Some Bibtex records splice a placeholder before the real URL; keep the first http(s) URL."""
    value = _strip(value)
    m = re.search(r"https?://\S+", value)
    return m.group(0).rstrip(".,;)") if m else value


def _paper_url(bib: str) -> str:
    """Resolve the paper's landing URL from its Bibtex: eprint -> arxiv, else url, else doi.

    eprint is only trusted when it is a syntactically valid arXiv id, so malformed
    placeholder values never produce a fabricated arxiv.org link.
    """
    eprint = _arxiv_id(_bib_field(bib, "eprint"))
    url = _first_url(_bib_field(bib, "url"))
    doi = _strip(_bib_field(bib, "doi"))
    if eprint:
        return f"https://arxiv.org/abs/{eprint}"
    if url:
        return url
    if doi:
        return f"https://doi.org/{doi}" if not doi.lower().startswith("http") else doi
    return ""


def _deep_link(url: str, page: str) -> str:
    """Page-level deep link for a paper URL. PDF hosts get '#page=N'; others fall back to the URL."""
    if not url:
        return ""
    page = _strip(page)
    base = ""
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^\s#?]+)", url)
    if m:
        base = f"https://arxiv.org/pdf/{m.group(1)}"
    elif "aclanthology.org" in url:
        base = url if url.lower().endswith(".pdf") else url.rstrip("/") + ".pdf"
    elif url.lower().endswith(".pdf"):
        base = url
    else:
        return url  # e.g. DOI landing pages / journal HTML: no page anchor available
    if page.isdigit():
        return f"{base}#page={page}"
    return base


def build_claims() -> dict:
    rows = read_csv(CLAIM_CSV)
    bib_by_key = {r["Citation_Key"]: _strip(r.get("Bibtex")) for r in read_csv(FINAL_TABLE)}
    url_by_key = {k: _paper_url(b) for k, b in bib_by_key.items()}

    slots = []
    for r in rows:
        slot = {k: _strip(r.get(k)) for k in CLAIM_FIELDS}
        url = url_by_key.get(slot["Citation_Key"], "")
        slot["Paper_URL"] = url
        slot["Claim_URL"] = _deep_link(url, slot["Claim_Page"])
        slot["Evidence_URL"] = _deep_link(url, slot["Evidence_Page"])
        slots.append(slot)

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

    corpus_keys = {s["Citation_Key"] for s in slots}
    with_url = sorted(k for k in corpus_keys if url_by_key.get(k))
    without_url = sorted(k for k in corpus_keys if not url_by_key.get(k))
    missing_ids = sorted({s["Paper_ID"] for s in slots if not url_by_key.get(s["Citation_Key"])},
                         key=lambda p: int(p) if p.isdigit() else 999)

    return {
        "n_slots": len(slots),
        "n_papers": summary["n_papers"],
        "slots": slots,
        "summary": summary,
        "papers_with_url": len(with_url),
        "papers_without_url": len(without_url),
        "papers_without_url_ids": missing_ids,
    }


# ------------------------------------------------------------------ stats -----

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


def _is_extended(r: dict) -> bool:
    return _strip(r.get("Interaction_Level")) == "Extended Dialogue"


def _is_dynamic(r: dict) -> bool:
    return _strip(r.get("Uses_Dynamic_State")).casefold() == "yes"


def _is_longitudinal(r: dict) -> bool:
    return _strip(r.get("Has_Longitudinal_Eval")).casefold() == "yes"


# Documented alias table for the free-text Clinical_Theory field. Each entry is
# (canonical family name, list of case-insensitive regexes). A paper counts once
# per family even if several of its reported strings map to the same family.
CLINICAL_THEORY_FAMILIES: list[tuple[str, list[str]]] = [
    (
        "CBT (cognitive-behavioral therapy)",
        [
            r"\bCBT\b",
            r"cognitive[- ]behavio",
            r"\bREBT\b",
            r"rational emotive",
            r"cognitive reframing",
            r"beck(?:'s)? cognitive theory",
            r"cognitive conceptuali",  # cognitive conceptualization (diagram)
            r"cognitive distortion",
            r"behavioral activation",
        ],
    ),
    (
        "Motivational interviewing",
        [
            r"motivational interviewing",
            r"\bMI\b",
            r"\bMITI\b",
            r"\bMISC\b",
            r"DARN",
            r"transtheoretical",
        ],
    ),
    ("Dialectical behavior therapy", [r"\bDBT\b", r"dialectical behavio"]),
    ("Problem-solving therapy", [r"problem[- ]solving", r"\bPST\b", r"ADAPT model"]),
    (
        "Working alliance",
        [r"\bWAI\b", r"\bWAIS\b", r"bordin", r"\bBLRI\b", r"\bCCS-R\b", r"working alliance"],
    ),
    ("Person-centered / Rogers", [r"rogers", r"person[- ]centered", r"client[- ]centered"]),
    ("Narrative therapy / IMCS", [r"narrative therapy", r"\bIMCS\b", r"inn?ovative moments"]),
    (
        "Diagnostic manuals & symptom scales",
        [
            r"\bDSM\b",
            r"\bICD\b",
            r"\bPHQ\b",
            r"\bGAD\b",
            r"\bBDI\b",
            r"\bPANSS\b",
            r"\bOQ-45\b",
            r"\bPDI\b",
            r"diagNostic and statistical",
        ],
    ),
    (
        "Crisis & suicide-risk frameworks",
        [r"crisis intervention", r"suicide", r"mhGAP", r"LIVE LIFE"],
    ),
    ("Big Five", [r"big five"]),
    (
        "Emotion / empathy constructs",
        [r"emotional labor", r"empathic resonance", r"relational empathy", r"emotion theory", r"empathy"],
    ),
    (
        "Clinical guidelines & exams",
        [
            r"NCMHCE",
            r"\bOSCE\b",
            r"ADHD clinical guidelines",
            r"counseling examination standards",
            r"\bSOAP\b",
        ],
    ),
]

CLINICAL_THEORY_SPLIT = re.compile(r"[;,+/、]| and ")


def _split_clinical_theory(raw: str) -> list[str]:
    tokens = []
    for t in CLINICAL_THEORY_SPLIT.split(raw):
        t = t.strip().strip(".;").strip()
        if t and t.casefold() not in {x.casefold() for x in tokens}:
            tokens.append(t)
    return tokens


def _match_families(raw: str) -> list[str]:
    matched = []
    for token in _split_clinical_theory(raw):
        for name, patterns in CLINICAL_THEORY_FAMILIES:
            if name in matched:
                continue
            if any(re.search(p, token, re.IGNORECASE) for p in patterns):
                matched.append(name)
    return matched


def _clinical_theory(ft: list[dict]) -> dict:
    denominator = len(ft)
    by_family: dict[str, list[str]] = {name: [] for name, _ in CLINICAL_THEORY_FAMILIES}
    unclassified: list[str] = []
    not_specified: list[str] = []
    raw_counts: dict[str, list[str]] = {}

    for r in ft:
        pid = r["Paper_ID"]
        raw = _strip(r.get("Clinical_Theory"))
        raw_counts.setdefault(raw, []).append(pid)
        if raw.casefold() == "not specified":
            not_specified.append(pid)
            continue
        matched = _match_families(raw)
        if not matched:
            unclassified.append(pid)
        for name in matched:
            by_family[name].append(pid)

    def sort_ids(ids: list[str]) -> list[str]:
        return sorted(set(ids), key=lambda p: int(p) if p.isdigit() else 999)

    families = [
        {"name": name, "n": len(sort_ids(ids)), "paper_ids": sort_ids(ids)}
        for name, ids in by_family.items()
        if ids
    ]
    families.sort(key=lambda f: (-f["n"], f["name"]))

    raw = [
        {"value": value, "n": len(ids), "paper_ids": sort_ids(ids)}
        for value, ids in sorted(raw_counts.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    ]

    return {
        "denominator": denominator,
        "multi_label": True,
        "families": families,
        "unclassified": {"n": len(sort_ids(unclassified)), "paper_ids": sort_ids(unclassified)},
        "not_specified": {"n": len(sort_ids(not_specified)), "paper_ids": sort_ids(not_specified)},
        "raw": raw,
        "mapping_note": (
            "Each free-text Clinical_Theory string is split on ';', ',', '+', '/', "
            "'、' and ' and ', then each fragment is matched (case-insensitively) "
            "against the documented alias table in web/build/build_data.py. "
            "A paper is counted once per family. Counts are multi-label and use "
            "the full corpus (n = 52) as the denominator, so families may sum to "
            "more than 52. Fragments that match no family are reported as "
            "'Unclassified'; the single paper that reports 'Not specified' is "
            "listed separately. The unmodified raw strings are preserved under 'raw'."
        ),
    }


def _behavioral_validity(ft: list[dict], definitions: dict[str, str]) -> dict:
    criteria_meta = [
        ("extended_dialogue", "Extended dialogue", "Interaction_Level", "Interaction_Level == 'Extended Dialogue'"),
        ("dynamic_state", "Dynamic user state", "Uses_Dynamic_State", "Uses_Dynamic_State == 'Yes'"),
        ("longitudinal", "Longitudinal evaluation", "Has_Longitudinal_Eval", "Has_Longitudinal_Eval == 'Yes'"),
    ]
    flags = {
        "extended_dialogue": _is_extended,
        "dynamic_state": _is_dynamic,
        "longitudinal": _is_longitudinal,
    }
    criteria = [
        {
            "id": cid,
            "label": label,
            "field": field,
            "rule": rule,
            "n": sum(1 for r in ft if flags[cid](r)),
            "definition": definitions.get(field, ""),
        }
        for cid, label, field, rule in criteria_meta
    ]

    combinations = []
    for ed, ds, lg in itertools.product([False, True], repeat=3):
        ids = [
            r["Paper_ID"]
            for r in ft
            if flags["extended_dialogue"](r) == ed
            and flags["dynamic_state"](r) == ds
            and flags["longitudinal"](r) == lg
        ]
        combinations.append(
            {
                "extended_dialogue": ed,
                "dynamic_state": ds,
                "longitudinal": lg,
                "n": len(ids),
                "paper_ids": ids,
            }
        )

    pairwise = []
    for a, b in itertools.combinations(["extended_dialogue", "dynamic_state", "longitudinal"], 2):
        both = [r["Paper_ID"] for r in ft if flags[a](r) and flags[b](r)]
        only_a = [r["Paper_ID"] for r in ft if flags[a](r) and not flags[b](r)]
        only_b = [r["Paper_ID"] for r in ft if not flags[a](r) and flags[b](r)]
        neither = [r["Paper_ID"] for r in ft if not flags[a](r) and not flags[b](r)]
        pairwise.append(
            {
                "a": a,
                "b": b,
                "both": len(both),
                "only_a": len(only_a),
                "only_b": len(only_b),
                "neither": len(neither),
            }
        )

    caveats = [
        "The three criteria are NOT nested: extended dialogue, dynamic user state and "
        "longitudinal evaluation are independent coded fields, so their counts (31, 13, 3) "
        "must not be drawn as a funnel or otherwise imply a subset relation.",
        "Of the 13 papers that model a dynamic user state, 2 are not extended dialogues: "
        "paper 65 (Short Multi-turn) and paper 111 (Longitudinal).",
        "Of the 3 papers with a longitudinal evaluation, 2 are not extended dialogues: "
        "paper 34 and paper 111 (both coded Longitudinal as their highest interaction level).",
        "10 papers are extended + dynamic but not longitudinal, and the extended + dynamic + "
        "longitudinal intersection contains a single paper (13).",
        "A longer dialogue does not by itself provide trajectory-level evidence "
        "(paper Sec. 4.2): interaction length and evidence about behavioral change "
        "across an interaction are separate properties.",
    ]
    return {
        "n": len(ft),
        "nested": False,
        "criteria": criteria,
        "combinations": combinations,
        "pairwise": pairwise,
        "caveats": caveats,
    }


def build_stats(codebook: list[dict]) -> dict:
    ft = read_csv(FINAL_TABLE)
    theory = read_csv(THEORY_CSV)
    n = len(ft)
    dims6 = ["Utility", "Fidelity", "Realism", "Emotional Plausibility", "Consistency", "Safety"]

    def cnt(col: str) -> int:
        return sum(1 for r in ft if yes(r, col))

    definitions = {f["name"]: f["definition"] for g in codebook for f in g["fields"]}

    ext = [r for r in ft if _is_extended(r)]
    tcounts = Counter()
    for r in theory:
        for t in (r.get("Theory_Eval_Type") or "").split(";"):
            t = t.strip()
            if t:
                tcounts[t] += 1

    rubric_ft = [r for r in ft if yes(r, "Has_Rubric")]
    rel_counts = Counter(_strip(r.get("Reliability_Reported")) or "(blank)" for r in ft)
    rel_with_rubric = Counter(_strip(r.get("Reliability_Reported")) or "(blank)" for r in rubric_ft)
    llm_ft = [r for r in ft if yes(r, "Eval_LLM_Judge")]
    llm_validated = sum(1 for r in llm_ft if yes(r, "LLM_Judge_Validated"))

    gated = [
        {
            "id": "llm_judge_validation",
            "field": "LLM_Judge_Validated",
            "gate_field": "Eval_LLM_Judge",
            "gate_value": "Yes",
            "label": "Validate the LLM judge against human judgments",
            "n": llm_validated,
            "denominator": len(llm_ft),
            "unconditional_n": cnt("LLM_Judge_Validated"),
            "note": (
                f"{llm_validated} of the {len(llm_ft)} papers that use an LLM judge "
                "(Eval_LLM_Judge = Yes) also validate the judge against human judgments. "
                "The unconditional count (24 across all 52 papers) must never be shown "
                "without stating that denominator."
            ),
        },
        {
            "id": "rubric_reliability",
            "field": "Reliability_Reported",
            "gate_field": "Has_Rubric",
            "gate_value": "Yes",
            "label": "Report inter-rater reliability",
            "n": rel_with_rubric.get("Yes", 0),
            "denominator": len(rubric_ft),
            "unconditional_n": rel_counts.get("Yes", 0),
            "note": (
                f"{rel_with_rubric.get('Yes', 0)} of the {len(rubric_ft)} papers that "
                "provide a rubric or scoring criteria (Has_Rubric = Yes) also report "
                "inter-rater reliability. The unconditional count (16 across all 52 papers) "
                "must never be shown without stating that denominator."
            ),
        },
    ]

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
        # kept for backwards compatibility; see behavioral_validity for the non-nested view
        "funnel": [
            {"name": "All reviewed papers", "n": n},
            {"name": "Evaluate extended dialogues", "n": len(ext)},
            {"name": "Model dynamic user state", "n": sum(1 for r in ft if _is_dynamic(r))},
            {"name": "Longitudinal evaluation", "n": sum(1 for r in ft if _is_longitudinal(r))},
        ],
        "behavioral_validity": _behavioral_validity(ft, definitions),
        "behavior_depth_extended": dict(Counter(_strip(r.get("Behavior_Eval_Depth")) for r in ext)),
        "gated": gated,
        "reliability_reporting": {
            "value_counts": {
                "Yes": rel_counts.get("Yes", 0),
                "No": rel_counts.get("No", 0),
                "N/A": rel_counts.get("N/A", 0),
            },
            "with_rubric": {
                "denominator": len(rubric_ft),
                "Yes": rel_with_rubric.get("Yes", 0),
                "No": rel_with_rubric.get("No", 0),
                "N/A": rel_with_rubric.get("N/A", 0),
            },
        },
        "clinical_theory": _clinical_theory(ft),
        "rubric": {
            "has": cnt("Has_Rubric"),
            "reported_reliability": sum(
                1 for r in ft if yes(r, "Has_Rubric") and yes(r, "Reliability_Reported")
            ),
        },
        "llm_judge": {
            "used": cnt("Eval_LLM_Judge"),
            "validated": llm_validated,
        },
        "prompt_disclosure": dict(Counter(_strip(r.get("Prompt_Disclosure")) for r in ft)),
        "theory_grounding": dict(Counter(_strip(r.get("Theory_Grounding")) for r in theory)),
        "theory_operationalized": dict(
            Counter(_strip(r.get("Theory_Operationalized_In_Evaluation")) for r in theory)
        ),
        "theory_eval_types": {t: tcounts.get(t, 0) for t in THEORY_EVAL_TYPES},
        "dims_ge1": sum(1 for r in ft if sum(1 for d in dims6 if yes(r, d)) >= 1),
        "dims_ge3": sum(1 for r in ft if sum(1 for d in dims6 if yes(r, d)) >= 3),
    }


# ------------------------------------------------------------- downloads ------


def copy_downloads() -> list[dict]:
    """Copy the four released source files byte-for-byte into web/downloads/."""
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    copied = []
    for src, name in DOWNLOAD_FILES:
        dst = DOWNLOADS / name
        shutil.copyfile(src, dst)
        copied.append(
            {
                "name": name,
                "source": str(src.relative_to(ROOT)),
                "bytes": dst.stat().st_size,
            }
        )
    return copied


# ------------------------------------------------------------------- main -----


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    codebook = parse_codebook()
    papers = build_papers(codebook)
    claims = build_claims()
    stats = build_stats(codebook)
    downloads = copy_downloads()

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
    dyn = Counter(p["values"]["Uses_Dynamic_State"] for p in papers["papers"])
    bv = stats["behavioral_validity"]
    gated = {g["id"]: g for g in stats["gated"]}

    print(f"codebook: {len(codebook)} groups, {nfields} fields")
    print(f"papers:   {papers['n']} papers x {len(papers['fields'])} fields")
    print(f"claims:   {claims['n_slots']} slots / {claims['n_papers']} papers; "
          f"papers_with_url={claims['papers_with_url']} papers_without_url={claims['papers_without_url']} "
          f"(missing Paper_IDs: {claims['papers_without_url_ids']})")
    print(f"stats:    grounding={stats['theory_grounding']} op={stats['theory_operationalized']}")
    print(f"Uses_Dynamic_State: {dict(dyn)}")
    print(
        "gated:    llm_judge_validation "
        f"{gated['llm_judge_validation']['n']}/{gated['llm_judge_validation']['denominator']} "
        f"(unconditional {gated['llm_judge_validation']['unconditional_n']}); "
        "rubric_reliability "
        f"{gated['rubric_reliability']['n']}/{gated['rubric_reliability']['denominator']} "
        f"(unconditional {gated['rubric_reliability']['unconditional_n']})"
    )
    print(f"reliability_reporting: {stats['reliability_reporting']}")
    print(
        "behavioral_validity criteria: "
        + ", ".join(f"{c['id']}={c['n']}" for c in bv["criteria"])
    )
    for row in bv["combinations"]:
        key = "".join("T" if row[k] else "F" for k in ("extended_dialogue", "dynamic_state", "longitudinal"))
        print(f"  combo {key}: n={row['n']} ids={row['paper_ids']}")
    for row in bv["pairwise"]:
        print(
            f"  pairwise {row['a']}&{row['b']}: both={row['both']} only_a={row['only_a']} "
            f"only_b={row['only_b']} neither={row['neither']}"
        )
    ct = stats["clinical_theory"]
    print(f"clinical_theory families (denominator {ct['denominator']}, multi-label):")
    for fam in ct["families"]:
        print(f"  {fam['n']:>2}  {fam['name']}  ids={fam['paper_ids']}")
    print(f"  unclassified: n={ct['unclassified']['n']} ids={ct['unclassified']['paper_ids']}")
    print(f"  not_specified: n={ct['not_specified']['n']} ids={ct['not_specified']['paper_ids']}")
    print("downloads:")
    for d in downloads:
        print(f"  web/downloads/{d['name']}  {d['bytes']} bytes  <- {d['source']}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
