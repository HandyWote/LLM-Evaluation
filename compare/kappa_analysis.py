"""
Inter-rater reliability analysis: Cohen's Kappa + heatmap.

Usage:
    uv run python compare/kappa_analysis.py
"""

import re
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

COMPARE_DIR = Path(__file__).parent
CXT_CSV = COMPARE_DIR / "cxt's evaluation.csv"
HYH_CSV = COMPARE_DIR / "hyh's evaluation.csv"
OUTPUT_DIR = COMPARE_DIR

# Fields to exclude from Kappa (metadata or free-text)
EXCLUDE_FIELDS = {
    "Paper_ID", "Citation_Key", "Bibtex", "Title", "Year", "Venue",
    # Free-text / open-ended fields (high cardinality, not categorical)
    "Domain",              # 35 unique values — free text
    "Focus_Type",          # 22 unique values — open classification
    "Temporal_Modeling_Details",  # 21 unique — free text descriptions
    "Raw Eval Metrics",    # 52 unique — raw metric names
    "Clinical_Theory",     # 47 unique — theory names
    "Agreement Method",    # 26 unique — method descriptions
}

# Normalize inconsistent value labels across raters
# Keys: cxt values → Values: canonical form (matching hyh's labels)
VALUE_NORMALIZE = {
    "FULL DISCLOSURE": "FULL",
    "PARTIAL DISCLOSURE": "PARTIAL",
    "NO DISCLOSURE": "NO",
}

# Column name fix: cxt has typo "Interention_Sensitivity"
COL_RENAME_CXT = {"Interention_Sensitivity": "Intervention_Sensitivity"}


def normalize_pid(pid: str) -> str:
    """Strip 综述 markers: '32(综述)' -> '32'."""
    if pd.isna(pid):
        return ""
    return re.sub(r"[（(]综述[）)]", "", str(pid).strip()).strip()


def load_and_join() -> pd.DataFrame:
    cxt = pd.read_csv(CXT_CSV, dtype=str).rename(columns=COL_RENAME_CXT)
    hyh = pd.read_csv(HYH_CSV, dtype=str)

    cxt["_pid"] = cxt["Paper_ID"].apply(normalize_pid)
    hyh["_pid"] = hyh["Paper_ID"].apply(normalize_pid)

    # Exclude review papers (综述)
    review_mask_cxt = cxt["Paper_ID"].str.contains("综述", na=False)
    review_mask_hyh = hyh["Paper_ID"].str.contains("综述", na=False)
    cxt = cxt[~review_mask_cxt].copy()
    hyh = hyh[~review_mask_hyh].copy()

    merged = cxt.merge(hyh, on="_pid", suffixes=("_cxt", "_hyh"))
    print(f"Merged: {len(merged)} papers (after excluding 综述)")
    return merged


def _analyze_disagreement(vals_cxt: pd.Series, vals_hyh: pd.Series,
                          n: int, disagree: int) -> str:
    """Analyze cross-tab to classify disagreement as systematic error vs conceptual difference."""
    ct = pd.crosstab(vals_cxt, vals_hyh)
    off_diag_cells = []
    for cxt_val in ct.index:
        for hyh_val in ct.columns:
            if cxt_val != hyh_val and ct.loc[cxt_val, hyh_val] > 0:
                off_diag_cells.append((ct.loc[cxt_val, hyh_val], cxt_val, hyh_val))
    off_diag_cells.sort(reverse=True)

    # Check for combined values
    combined_cxt = vals_cxt.str.contains("/", na=False).sum()

    # Check if one rater uses labels the other doesn't
    hyh_labels = set(vals_hyh.value_counts().index)
    cxt_labels = set(vals_cxt.value_counts().index)
    hyh_only = hyh_labels - cxt_labels

    parts = []

    # Top disagreement pattern
    if off_diag_cells:
        count, cxt_val, hyh_val = off_diag_cells[0]
        parts.append(f"cxt 标 {cxt_val} 的 {count} 篇中 hyh 标了 {hyh_val}")
    if len(off_diag_cells) > 1:
        count, cxt_val, hyh_val = off_diag_cells[1]
        parts.append(f"cxt 标 {cxt_val} 的 {count} 篇中 hyh 标了 {hyh_val}")

    # Combined values note
    if combined_cxt > 2:
        parts.append(f"cxt 有 {combined_cxt} 篇用了组合值")

    # Unique labels note
    if hyh_only:
        parts.append(f"hyh 使用了 cxt 没用的选项({', '.join(sorted(hyh_only))})")

    if not parts:
        parts.append(f"{disagree}/{n} 篇有分歧")

    return "；".join(parts)


# Classification of each field's disagreement nature
# "systematic" = one rater's threshold is miscalibrated, needs correction
# "conceptual" = definition ambiguity, both interpretations defensible
FIELD_DISAGREEMENT_NATURE = {
    # Systematic errors: cxt too permissive
    "Safety": "系统性错误",
    "LLM_Judge_Validated": "系统性错误",
    "Reliability_Reported": "系统性错误",
    "Has_Robustness_Testing": "系统性错误",
    "Has_Failure_Analysis": "系统性错误",
    "Uses_Dynamic_State": "系统性错误",
    "Intervention_Sensitivity": "系统性错误",
    "Eval_Automatic": "系统性错误",
    "Consistency": "系统性错误",
    "Coding Options": "系统性错误",
    # Conceptual differences: definition ambiguity
    "Behavior_Eval_Depth": "概念理解差异",
    "Persona_Model_Depth": "概念理解差异",
    "Prompt_Disclosure": "概念理解差异",
    "Interaction_Level": "概念理解差异",
    "Theory_Grounding": "概念理解差异",
    "Theory_Operationalized": "概念理解差异",
    "Fidelity": "概念理解差异",
    "Has_Rubric": "概念理解差异",
    "Has_Longitudinal_Eval": "概念理解差异",
    "Emotional Plausibility": "概念理解差异",
    "Sim_Behavior_Realistic": "概念理解差异",
    "Realism": "概念理解差异",
    "Simulation_Target": "概念理解差异",
    # Both raters similar, minor calibration
    "Utility": "轻微校准差异",
    "Comparable_To_Prior_Work": "轻微校准差异",
    "Human Learning / Outcomes": "轻微校准差异",
    "Uses_Standard_Metrics": "轻微校准差异",
    "Dataset_Available": "轻微校准差异",
    "Eval_Lay_Users": "轻微校准差异",
    "Eval_Human_Experts": "轻微校准差异",
    "Eval_LLM_Judge": "轻微校准差异",
    "Eval_User_Study": "轻微校准差异",
    "Metric_Interpretable": "无变异",
}



def compute_kappa(merged: pd.DataFrame) -> list[dict]:
    """Compute Cohen's Kappa for each eligible field."""
    results = []
    # Get all base field names (without _cxt/_hyh suffix)
    fields = set()
    for col in merged.columns:
        if col.endswith("_cxt"):
            base = col[:-4]
            if base not in EXCLUDE_FIELDS and f"{base}_hyh" in merged.columns:
                fields.add(base)

    for field in sorted(fields):
        col_cxt = f"{field}_cxt"
        col_hyh = f"{field}_hyh"
        df = merged[[col_cxt, col_hyh]].dropna()
        if len(df) < 2:
            continue

        # Normalize: strip whitespace, uppercase for boolean fields
        vals_cxt = df[col_cxt].str.strip().str.upper().replace(VALUE_NORMALIZE)
        vals_hyh = df[col_hyh].str.strip().str.upper().replace(VALUE_NORMALIZE)

        # Replace empty strings with NaN and drop
        mask = (vals_cxt != "") & (vals_hyh != "")
        vals_cxt = vals_cxt[mask]
        vals_hyh = vals_hyh[mask]
        n = len(vals_cxt)
        if n < 2:
            continue

        agreement = (vals_cxt.values == vals_hyh.values).sum()
        disagree = n - agreement
        kappa = cohen_kappa_score(vals_cxt.values, vals_hyh.values)

        # Analyze disagreement pattern for reason
        all_labels = set(vals_cxt.values) | set(vals_hyh.values)
        if len(all_labels) < 2:
            results.append({
                "field": field,
                "kappa": float("nan"),
                "agreement_rate": round(agreement / n, 3),
                "n": n,
                "n_disagree": disagree,
                "note": "single label — no variance",
                "reason": "cxt 全标同一值，无变异，无法计算 kappa",
                "nature": "无变异",
            })
            continue

        reason = _analyze_disagreement(vals_cxt, vals_hyh, n, disagree)
        nature = FIELD_DISAGREEMENT_NATURE.get(field, "未分类")

        results.append({
            "field": field,
            "kappa": round(kappa, 3),
            "agreement_rate": round(agreement / n, 3),
            "n": n,
            "n_disagree": disagree,
            "reason": reason,
            "nature": nature,
        })

    results.sort(key=lambda x: x["kappa"])
    return results


def main():
    merged = load_and_join()
    results = compute_kappa(merged)

    # Print summary table
    print(f"\n{'Field':<35} {'Kappa':>7} {'Agree%':>8} {'N':>4} {'Disagree':>9}")
    print("-" * 65)
    for r in results:
        note = f"  ({r['note']})" if r.get("note") else ""
        flag = " ***" if r["kappa"] == r["kappa"] and r["kappa"] < 0.6 else ""
        nature = r.get("nature", "")
        reason = f"  # {r['reason']}" if r.get("reason") else ""
        print(f"{r['field']:<35} {r['kappa']:>7.3f} {r['agreement_rate']:>7.1%} {r['n']:>4} {r['n_disagree']:>9}  {nature:<10}{flag}{note}{reason}")

    # Save CSV
    csv_path = OUTPUT_DIR / "kappa_results.csv"
    pd.DataFrame(results).to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")


if __name__ == "__main__":
    main()
