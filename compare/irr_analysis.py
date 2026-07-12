"""
Inter-Rater Reliability Analysis — all coded fields except metadata/ID.

Computes raw agreement, weighted/standard Cohen's kappa, confusion matrices,
missing data report, and methodological summary for the paper.

Usage:
    uv run python compare/irr_analysis.py
"""

import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

# Add project root so we can import lib.schemas
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from lib.schemas import BOOL_FIELDS, SINGLE_CHOICE_FIELDS, INTERNAL_TO_CSV  # noqa: E402

COMPARE_DIR = Path(__file__).parent
CXT_CSV = COMPARE_DIR / "cxt's evaluation.csv"
HYH_CSV = COMPARE_DIR / "hyh's evaluation.csv"
OUTPUT_DIR = COMPARE_DIR

# Column name typo fix in cxt
COL_RENAME_CXT = {"Interention_Sensitivity": "Intervention_Sensitivity"}

# ── Exclusions ──────────────────────────────────────────────────────────────
# Only exclude pure metadata/ID fields. All coded fields get IRR.
METADATA_INTERNAL = {"paper_id", "citation_key", "bibtex", "title", "year", "venue"}

# ── Ordinal field definitions (order = low → high) ──────────────────────────
# Fields in SINGLE_CHOICE_FIELDS that have a natural order get weighted kappa.
ORDINAL_CONFIG: dict[str, list[str]] = {
    "persona_model_depth": [
        "SURFACE PERSONA", "BEHAVIORAL STATE MODEL", "COGNITIVE MODEL",
        "DYNAMIC TRAITS", "EXPERT PRINCIPLES",
    ],
    "theory_operationalized": ["NONE", "MENTIONED", "PARTIAL", "STRONG"],
    "behavior_eval_depth": ["NONE", "STATIC", "PATTERN-LEVEL", "DYNAMIC"],
    "interaction_level": [
        "SINGLE-TURN", "SHORT MULTI-TURN", "EXTENDED DIALOGUE", "LONGITUDINAL",
    ],
    "prompt_disclosure": ["NO", "PARTIAL", "FULL"],
    "theory_grounding": ["NONE", "WEAK", "STRONG"],
}

# ── Value normalization ─────────────────────────────────────────────────────
# Applied before any comparison.
VALUE_NORMALIZE = {
    "FULL DISCLOSURE": "FULL",
    "PARTIAL DISCLOSURE": "PARTIAL",
    "NO DISCLOSURE": "NO",
    "NO DISCLOSURE": "NO",
}


# ── Build variable list from schemas ────────────────────────────────────────

def build_variable_list() -> list[dict]:
    """Auto-generate the variable config from lib/schemas.py."""
    variables = []

    # Boolean fields → binary kappa
    for internal_name in BOOL_FIELDS:
        if internal_name in METADATA_INTERNAL:
            continue
        csv_col = INTERNAL_TO_CSV.get(internal_name, internal_name)
        variables.append({
            "internal": internal_name,
            "csv_col": csv_col,
            "type": "binary",
            "statistic": "Cohen's kappa",
            "categories_display": "Yes / No",
        })

    # Single-choice fields → ordinal (weighted) or nominal (unweighted) kappa
    for internal_name, options in SINGLE_CHOICE_FIELDS.items():
        if internal_name in METADATA_INTERNAL:
            continue
        csv_col = INTERNAL_TO_CSV.get(internal_name, internal_name)

        if internal_name in ORDINAL_CONFIG:
            ordered = ORDINAL_CONFIG[internal_name]
            rank = {label: i for i, label in enumerate(ordered)}
            variables.append({
                "internal": internal_name,
                "csv_col": csv_col,
                "type": "ordinal",
                "statistic": "Linearly weighted Cohen's kappa",
                "categories_display": " / ".join(options),
                "rank": rank,
            })
        else:
            # Nominal multi-category → standard kappa
            variables.append({
                "internal": internal_name,
                "csv_col": csv_col,
                "type": "nominal",
                "statistic": "Cohen's kappa",
                "categories_display": " / ".join(options),
            })

    return variables


VARIABLES = build_variable_list()


# ── Data Loading ───────────────────────────────────────────────────────────

def normalize_pid(pid: str) -> str:
    """Strip 综述 markers: '32(综述)' -> '32'."""
    if pd.isna(pid):
        return ""
    return re.sub(r"[（(]综述[）)]", "", str(pid).strip()).strip()


def load_and_validate(csv_path: Path, rater_name: str) -> pd.DataFrame:
    """Load CSV, filter to valid rows (numeric Paper_ID), report drops."""
    df = pd.read_csv(csv_path, dtype=str).rename(columns=COL_RENAME_CXT)
    total = len(df)

    # Filter: keep only rows with numeric Paper_ID
    valid_mask = pd.to_numeric(df["Paper_ID"], errors="coerce").notna()
    n_dropped = total - valid_mask.sum()
    if n_dropped > 0:
        print(f"[{rater_name}] 丢弃 {n_dropped}/{total} 无效行 (Paper_ID 非数字)")

    df = df[valid_mask].copy()

    # Exclude review papers (综述)
    review_mask = df["Paper_ID"].str.contains("综述", na=False)
    n_review = review_mask.sum()
    if n_review > 0:
        print(f"[{rater_name}] 排除 {n_review} 篇综述")
    df = df[~review_mask].copy()

    df["_pid"] = df["Paper_ID"].apply(normalize_pid)
    print(f"[{rater_name}] 有效论文: {len(df)}")
    return df


# ── Label Normalization ────────────────────────────────────────────────────

def normalize_labels(series: pd.Series, normalize_map: dict | None = None) -> pd.Series:
    """Apply strip + upper + custom value normalization."""
    s = series.str.strip().str.upper().replace(VALUE_NORMALIZE)
    if normalize_map:
        s = s.replace(normalize_map)
    return s


def is_missing(s: pd.Series) -> pd.Series:
    """True if value is NaN or empty string after stripping."""
    return s.isna() | (s.str.strip() == "")


# ── Analysis Functions ─────────────────────────────────────────────────────

def analyze_variable(merged: pd.DataFrame, var_config: dict) -> dict:
    """Run full analysis for one variable. Returns a dict with all results."""
    col = var_config["csv_col"]
    col_cxt = f"{col}_cxt"
    col_hyh = f"{col}_hyh"

    # Check columns exist
    if col_cxt not in merged.columns or col_hyh not in merged.columns:
        return _skip_result(var_config, f"CSV 列缺失: {col}")

    # Missing data report (before any drop)
    missing_cxt = is_missing(merged[col_cxt]).sum()
    missing_hyh = is_missing(merged[col_hyh]).sum()
    missing_both = (is_missing(merged[col_cxt]) & is_missing(merged[col_hyh])).sum()
    total_papers = len(merged)

    # Normalize labels
    vals_cxt = normalize_labels(merged[col_cxt])
    vals_hyh = normalize_labels(merged[col_hyh])

    # Drop rows where either rater is missing
    valid = ~(is_missing(merged[col_cxt]) | is_missing(merged[col_hyh]))
    vals_cxt = vals_cxt[valid]
    vals_hyh = vals_hyh[valid]
    n = len(vals_cxt)

    if n < 2:
        return _skip_result(var_config, "有效样本 < 2")

    # Raw agreement
    n_agree = (vals_cxt.values == vals_hyh.values).sum()
    n_disagree = n - n_agree
    agreement_pct = round(n_agree / n * 100, 1)

    # Kappa
    kappa = float("nan")
    if var_config["type"] == "ordinal":
        kappa = _compute_weighted_kappa(vals_cxt, vals_hyh, var_config["rank"])
    else:
        # Binary or nominal: standard unweighted kappa
        if vals_cxt.nunique() > 1 or vals_hyh.nunique() > 1:
            kappa = round(cohen_kappa_score(vals_cxt.values, vals_hyh.values), 3)

    # Confusion matrix
    ct = pd.crosstab(
        vals_cxt.rename("cxt"),
        vals_hyh.rename("hyh"),
        dropna=False,
    )

    # Disagreement detail
    disagreement_detail = _analyze_disagreements(
        vals_cxt, vals_hyh, var_config, n, n_disagree
    )

    return {
        "csv_col": col,
        "display_name": col,
        "categories_display": var_config["categories_display"],
        "statistic": var_config["statistic"],
        "type": var_config["type"],
        "n_total": total_papers,
        "n_valid": n,
        "missing_cxt": missing_cxt,
        "missing_hyh": missing_hyh,
        "missing_both": missing_both,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "agreement_pct": agreement_pct,
        "kappa": kappa,
        "confusion_matrix": ct,
        "disagreement_detail": disagreement_detail,
        "note": "",
    }


def _compute_weighted_kappa(vals_cxt, vals_hyh, rank_map: dict) -> float:
    """Map labels to integer ranks and compute linearly weighted kappa."""
    y_cxt = vals_cxt.map(rank_map)
    y_hyh = vals_hyh.map(rank_map)
    valid_rank = y_cxt.notna() & y_hyh.notna()
    n_valid = valid_rank.sum()
    if n_valid < 2:
        return float("nan")
    if y_cxt[valid_rank].nunique() <= 1 and y_hyh[valid_rank].nunique() <= 1:
        return float("nan")
    return round(
        cohen_kappa_score(
            y_cxt[valid_rank].values,
            y_hyh[valid_rank].values,
            weights="linear",
        ),
        3,
    )


def _skip_result(var_config: dict, note: str) -> dict:
    """Return a placeholder for unanalyzable fields."""
    return {
        "csv_col": var_config["csv_col"],
        "display_name": var_config["csv_col"],
        "categories_display": var_config.get("categories_display", ""),
        "statistic": var_config.get("statistic", ""),
        "type": var_config.get("type", ""),
        "n_total": 0,
        "n_valid": 0,
        "missing_cxt": 0,
        "missing_hyh": 0,
        "missing_both": 0,
        "n_agree": 0,
        "n_disagree": 0,
        "agreement_pct": float("nan"),
        "kappa": float("nan"),
        "confusion_matrix": pd.DataFrame(),
        "disagreement_detail": "",
        "note": note,
    }


def _analyze_disagreements(
    vals_cxt: pd.Series,
    vals_hyh: pd.Series,
    var_config: dict,
    n: int,
    n_disagree: int,
) -> str:
    """Build a human-readable disagreement summary."""
    ct = pd.crosstab(vals_cxt, vals_hyh)
    off_diag = []
    for cxt_val in ct.index:
        for hyh_val in ct.columns:
            if cxt_val != hyh_val and ct.loc[cxt_val, hyh_val] > 0:
                off_diag.append((ct.loc[cxt_val, hyh_val], cxt_val, hyh_val))
    off_diag.sort(reverse=True)

    parts = []
    if off_diag:
        count, cxt_val, hyh_val = off_diag[0]
        parts.append(f"{cxt_val}→{hyh_val} ({count}篇)")
    if len(off_diag) > 1:
        count, cxt_val, hyh_val = off_diag[1]
        parts.append(f"{cxt_val}→{hyh_val} ({count}篇)")

    # Ordinal-specific: adjacent vs. extreme
    if var_config["type"] == "ordinal" and "rank" in var_config:
        rank = var_config["rank"]
        vals_cxt_r = vals_cxt.map(rank)
        vals_hyh_r = vals_hyh.map(rank)
        disagree_mask = vals_cxt_r != vals_hyh_r
        diffs = (vals_cxt_r[disagree_mask] - vals_hyh_r[disagree_mask]).abs()
        adjacent = (diffs == 1).sum()
        extreme = (diffs >= 2).sum()
        if adjacent > 0:
            parts.append(f"相邻分歧({adjacent})")
        if extreme > 0:
            parts.append(f"极端分歧({extreme})")

    if not parts:
        parts.append(f"{n_disagree}/{n} 篇分歧")

    return "；".join(parts)


# ── Output Generation ──────────────────────────────────────────────────────

def print_missing_report(results: list[dict]):
    """Print missing data summary table (only fields with any missing)."""
    with_missing = [r for r in results if r["n_total"] > 0
                    and (r["missing_cxt"] + r["missing_hyh"] > 0)]
    if not with_missing:
        print("\n所有字段无缺失数据。")
        return

    print("\n" + "=" * 90)
    print("缺失数据报告（仅显示有缺失的字段）")
    print("=" * 90)
    header = f"{'变量':<38} {'总计':>5} {'有效':>5} {'cxt缺':>6} {'hyh缺':>6} {'双方缺':>6}"
    print(header)
    print("-" * 90)
    for r in with_missing:
        print(
            f"{r['display_name']:<38} {r['n_total']:>5} {r['n_valid']:>5} "
            f"{r['missing_cxt']:>6} {r['missing_hyh']:>6} {r['missing_both']:>6}"
        )


def print_results_table(results: list[dict]):
    """Print the main results table."""
    valid = [r for r in results if r["n_valid"] > 0]
    skipped = [r for r in results if r["n_valid"] == 0]

    print("\n" + "=" * 100)
    print(f"Inter-Rater Reliability Results ({len(valid)} fields)")
    print("=" * 100)
    header = (
        f"{'Field':<38} {'Type':<10} {'Agree%':>7} {'Kappa':>7}  {'Disagreement'}"
    )
    print(header)
    print("-" * 100)
    for r in sorted(valid, key=lambda x: (x["kappa"] if x["kappa"] == x["kappa"] else -999)):
        kappa_str = f"{r['kappa']:.3f}" if r["kappa"] == r["kappa"] else "N/A"
        agree_str = f"{r['agreement_pct']:.1f}%" if r["agreement_pct"] == r["agreement_pct"] else "N/A"
        flag = " ⚠" if r["kappa"] == r["kappa"] and r["kappa"] < 0.4 else ""
        print(
            f"{r['display_name']:<38} {r['type']:<10} {agree_str:>7} {kappa_str:>7}{flag}  "
            f"{r['disagreement_detail']}"
        )

    valid_kappas = [r["kappa"] for r in valid if r["kappa"] == r["kappa"]]
    valid_agrees = [r["agreement_pct"] for r in valid if r["agreement_pct"] == r["agreement_pct"]]
    if valid_kappas:
        print(f"\nKappa range: {min(valid_kappas):.3f} – {max(valid_kappas):.3f}")
    if valid_agrees:
        print(f"Raw agreement range: {min(valid_agrees):.1f}% – {max(valid_agrees):.1f}%")

    if skipped:
        print(f"\n跳过字段 ({len(skipped)}):")
        for r in skipped:
            print(f"  {r['display_name']}: {r['note']}")


def print_confusion_matrices(results: list[dict]):
    """Print confusion matrix for each variable."""
    print("\n" + "=" * 90)
    print("混淆矩阵 (Confusion Matrices)")
    print("=" * 90)
    for r in results:
        if r["n_valid"] == 0:
            continue
        print(f"\n── {r['display_name']} ──")
        print(r["confusion_matrix"].to_string())
        print(f"  分歧: {r['disagreement_detail']}")


def generate_method_summary(results: list[dict]) -> str:
    """Generate the methodological summary paragraph for the paper."""
    valid = [r for r in results if r["n_valid"] > 0 and r["kappa"] == r["kappa"]]
    ordinal_vars = [r["csv_col"] for r in results if r["type"] == "ordinal"]
    valid_agrees = [r["agreement_pct"] for r in valid if r["agreement_pct"] == r["agreement_pct"]]

    min_agree = min(valid_agrees)
    max_agree = max(valid_agrees)
    min_k = min(r["kappa"] for r in valid)
    max_k = max(r["kappa"] for r in valid)

    ordinal_names = ", ".join(ordinal_vars)

    return (
        f"Two researchers independently coded all 52 papers using a predefined "
        f"38-field codebook. Inter-rater agreement was assessed on the original "
        f"pre-adjudication labels across {len(valid)} coded fields. We report both "
        f"raw agreement and Cohen's kappa, using weighted kappa (linear weighting "
        f"scheme) for ordinal variables ({ordinal_names}) and standard kappa for "
        f"binary and nominal variables. Across all coded dimensions, raw agreement "
        f"ranged from {min_agree:.1f}% to {max_agree:.1f}%, and kappa ranged from "
        f"{min_k:.3f} to {max_k:.3f}. Remaining disagreements were resolved through "
        f"discussion with the faculty lead to produce the final consensus coding."
    )


def generate_data_notes(results: list[dict]) -> str:
    """Generate data quality and label cleaning notes."""
    lines = [
        "# IRR Data Notes",
        "",
        "## Label Cleaning",
        "",
        "1. **Case normalization**: All labels were uppercased and whitespace-stripped.",
        "   cxt used mixed case (Yes/No), hyh used uppercase (YES/NO).",
        "2. **Column name typo**: cxt's `Interention_Sensitivity` (missing 'v') was",
        "   renamed to `Intervention_Sensitivity` to match hyh's column.",
        "3. **Prompt_Disclosure normalization**: cxt's `FULL DISCLOSURE`/`PARTIAL DISCLOSURE`",
        "   /`NO DISCLOSURE` were normalized to `FULL`/`PARTIAL`/`NO`.",
        "",
        "## Ordinal Variables (Weighted Kappa)",
        "",
    ]
    ordinal = [r for r in results if r["type"] == "ordinal"]
    for r in ordinal:
        lines.append(f"- **{r['csv_col']}**: categories = {r['categories_display']}")
        lines.append(f"  Kappa = {r['kappa']}, Agreement = {r['agreement_pct']}%")

    lines += [
        "",
        "## Data Quality Issues in cxt CSV",
        "",
        "The cxt CSV file contained corrupted rows beyond the 52 valid papers.",
        "Rows with non-numeric Paper_ID were filtered out during loading.",
        "",
        "## Missing Data Summary",
        "",
        "Missing values are treated as NA and excluded pairwise from kappa computation.",
        "No imputation was performed.",
        "",
    ]

    # Missing data table
    lines.append(
        "| Variable | Total | Valid | Missing cxt | Missing hyh | Missing both |"
    )
    lines.append(
        "|----------|-------|-------|-------------|-------------|--------------|"
    )
    for r in results:
        if r["n_total"] > 0:
            lines.append(
                f"| {r['display_name']} | {r['n_total']} | {r['n_valid']} | "
                f"{r['missing_cxt']} | {r['missing_hyh']} | {r['missing_both']} |"
            )

    return "\n".join(lines)


def save_outputs(results: list[dict]):
    """Save all output files."""
    valid = [r for r in results if r["n_valid"] > 0]

    # 1. irr_results.csv
    rows = []
    for r in valid:
        rows.append({
            "Field": r["display_name"],
            "Type": r["type"],
            "Categories": r["categories_display"],
            "Statistic": r["statistic"],
            "Raw agreement (%)": r["agreement_pct"],
            "Kappa": r["kappa"],
            "N": r["n_valid"],
            "N disagree": r["n_disagree"],
            "Disagreement detail": r["disagreement_detail"],
        })
    df_results = pd.DataFrame(rows)
    path = OUTPUT_DIR / "irr_results.csv"
    df_results.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved: {path}")

    # 2. irr_confusion_matrices.csv (long format)
    cm_rows = []
    for r in valid:
        ct = r["confusion_matrix"]
        if ct.empty:
            continue
        for cxt_val in ct.index:
            for hyh_val in ct.columns:
                cm_rows.append({
                    "variable": r["display_name"],
                    "cxt_value": cxt_val,
                    "hyh_value": hyh_val,
                    "count": int(ct.loc[cxt_val, hyh_val]),
                })
    if cm_rows:
        df_cm = pd.DataFrame(cm_rows)
        path_cm = OUTPUT_DIR / "irr_confusion_matrices.csv"
        df_cm.to_csv(path_cm, index=False, encoding="utf-8-sig")
        print(f"Saved: {path_cm}")

    # 3. irr_method_summary.md
    summary = generate_method_summary(results)
    path_summary = OUTPUT_DIR / "irr_method_summary.md"
    path_summary.write_text("# Methodological Summary\n\n" + summary, encoding="utf-8")
    print(f"Saved: {path_summary}")

    # 4. irr_data_notes.md
    notes = generate_data_notes(results)
    path_notes = OUTPUT_DIR / "irr_data_notes.md"
    path_notes.write_text(notes, encoding="utf-8")
    print(f"Saved: {path_notes}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Inter-Rater Reliability Analysis — All Coded Fields")
    print("=" * 60)
    print(f"Fields to analyze: {len(VARIABLES)}")

    # 1. Load and validate
    cxt = load_and_validate(CXT_CSV, "cxt")
    hyh = load_and_validate(HYH_CSV, "hyh")

    # 2. Merge
    merged = cxt.merge(hyh, on="_pid", suffixes=("_cxt", "_hyh"))
    print(f"\n合并后论文数: {len(merged)}")

    # 3. Analyze each variable
    results = []
    for var_config in VARIABLES:
        result = analyze_variable(merged, var_config)
        results.append(result)

    # 4. Output reports
    print_missing_report(results)
    print_results_table(results)
    print_confusion_matrices(results)

    # 5. Methodological summary
    print("\n" + "=" * 90)
    print("方法论段落 (Methodological Summary)")
    print("=" * 90)
    summary = generate_method_summary(results)
    print("\n" + summary)

    # 6. Save all outputs
    print("\n" + "=" * 60)
    print("保存输出文件")
    print("=" * 60)
    save_outputs(results)

    print("\n✓ 分析完成")


if __name__ == "__main__":
    main()
