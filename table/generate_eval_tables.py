#!/usr/bin/env python3
"""
Generate evaluation methodology LaTeX tables from final-table.csv.

Usage:
    cd table
    uv run python generate_eval_tables.py

Output:
    table/eval_tables.tex           - Main tables (counts only)
    table/eval_tables_citations.tex - Citation companion tables
"""

import csv
from pathlib import Path


def read_data(csv_path: str) -> list[dict]:
    """Read CSV file and return list of dicts."""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def cite_keys(papers: list[str]) -> str:
    """Format citation keys as LaTeX \\cite{} commands."""
    if not papers:
        return "---"
    return ", ".join(f"\\cite{{{p}}}" for p in sorted(papers))


def yes_papers(rows: list[dict], col: str) -> list[str]:
    """Get sorted Citation_Key list where column == 'Yes'."""
    return sorted(r["Citation_Key"] for r in rows if r.get(col, "").strip() == "Yes")


def cross_tab(rows: list[dict], col1: str, col2: str) -> dict[tuple[str, str], list[str]]:
    """Build cross-tabulation: (val1, val2) -> sorted list of Citation_Key."""
    result: dict[tuple[str, str], list[str]] = {}
    for r in rows:
        v1 = r.get(col1, "").strip()
        v2 = r.get(col2, "").strip()
        if v1 and v2:
            result.setdefault((v1, v2), []).append(r["Citation_Key"])
    return {k: sorted(v) for k, v in result.items()}


def triple_tab(rows: list[dict], col1: str, col2: str, col3: str) -> dict[tuple[str, str, str], list[str]]:
    """Build 3-way cross-tabulation."""
    result: dict[tuple[str, str, str], list[str]] = {}
    for r in rows:
        v1 = r.get(col1, "").strip()
        v2 = r.get(col2, "").strip()
        v3 = r.get(col3, "").strip()
        if v1 and v2 and v3:
            result.setdefault((v1, v2, v3), []).append(r["Citation_Key"])
    return {k: sorted(v) for k, v in result.items()}


def _classify_paper_row(row: dict, longi_keys: set[str]) -> str:
    """Classify paper into Interaction Level row, handling longitudinal override."""
    ck = row.get("Citation_Key", "").strip()
    if ck in longi_keys:
        return "Longitudinal"
    return row.get("Interaction_Level", "").strip()


def _classify_paper_col(row: dict) -> str:
    """Classify paper into column: Static, Pattern-level, Dynamic, or (unspecified)."""
    uds = row.get("Uses_Dynamic_State", "").strip().lower()
    bed = row.get("Behavior_Eval_Depth", "").strip()
    if uds == "yes":
        return "Dynamic"
    if bed == "Static":
        return "Static"
    if bed == "Pattern-level":
        return "Pattern-level"
    return "(unspecified)"


def _table4_data(rows: list[dict]) -> dict[tuple[str, str], list[str]]:
    """Build cross-tab for Table 4 using Uses_Dynamic_State and Has_Longitudinal_Eval."""
    longi_keys = {
        r["Citation_Key"] for r in rows
        if r.get("Has_Longitudinal_Eval", "").strip() == "Yes"
    }
    result: dict[tuple[str, str], list[str]] = {}
    for r in rows:
        row_label = _classify_paper_row(r, longi_keys)
        col_label = _classify_paper_col(r)
        result.setdefault((row_label, col_label), []).append(r["Citation_Key"])
    return {k: sorted(v) for k, v in result.items()}


# ---------------------------------------------------------------------------
# Table 1: Evaluator Type Distribution
# ---------------------------------------------------------------------------

def generate_table1_main(rows: list[dict]) -> str:
    total = len(rows)
    types = [
        ("Human Experts", "Eval_Human_Experts"),
        ("LLM Judges", "Eval_LLM_Judge"),
        ("Automatic Metrics", "Eval_Automatic"),
    ]

    all_three = sorted(
        r["Citation_Key"] for r in rows
        if r.get("Eval_Human_Experts", "").strip() == "Yes"
        and r.get("Eval_LLM_Judge", "").strip() == "Yes"
        and r.get("Eval_Automatic", "").strip() == "Yes"
    )

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lc}
\toprule
\textbf{Evaluator Type} & \textbf{Count (\%)} \\
\midrule
"""
    for label, col in types:
        papers = yes_papers(rows, col)
        pct = len(papers) / total * 100
        latex += f"{label} & {len(papers)} ({pct:.1f}\\%) \\\\\n"

    pct_all = len(all_three) / total * 100
    latex += f"All Three (Expert + LLM + Auto) & {len(all_three)} ({pct_all:.1f}\\%) \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Distribution of Evaluator Types Across Studies ($N=%d$)}
\label{tab:evaluator-types}
\end{table*}
""" % total
    return latex


def generate_table1_cite(rows: list[dict]) -> str:
    types = [
        ("Human Experts", "Eval_Human_Experts"),
        ("LLM Judges", "Eval_LLM_Judge"),
        ("Automatic Metrics", "Eval_Automatic"),
    ]

    all_three = sorted(
        r["Citation_Key"] for r in rows
        if r.get("Eval_Human_Experts", "").strip() == "Yes"
        and r.get("Eval_LLM_Judge", "").strip() == "Yes"
        and r.get("Eval_Automatic", "").strip() == "Yes"
    )

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5cm}p{10cm}}
\toprule
\textbf{Evaluator Type} & \textbf{Papers} \\
\midrule
"""
    for label, col in types:
        papers = yes_papers(rows, col)
        latex += f"{label} & {cite_keys(papers)} \\\\\n\\midrule\n"

    latex += f"All Three (Expert + LLM + Auto) & {cite_keys(all_three)} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Evaluator Type}
\label{tab:evaluator-types-cite}
\end{table*}
"""
    return latex


# ---------------------------------------------------------------------------
# Table 2: Rubric Use × Reliability Reporting
# ---------------------------------------------------------------------------

def generate_table2_main(rows: list[dict]) -> str:
    tab = cross_tab(rows, "Has_Rubric", "Reliability_Reported")
    order = [("Yes", "Yes"), ("Yes", "No"), ("No", "Yes"), ("No", "No")]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{llc}
\toprule
\textbf{Has Rubric} & \textbf{Reliability Reported} & \textbf{Count} \\
\midrule
"""
    for rubric, rel in order:
        papers = tab.get((rubric, rel), [])
        latex += f"{rubric} & {rel} & {len(papers)} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Scoring Rubric and Inter-Rater Reliability Reporting}
\label{tab:rubric-reliability}
\end{table*}
"""
    return latex


def generate_table2_cite(rows: list[dict]) -> str:
    tab = cross_tab(rows, "Has_Rubric", "Reliability_Reported")
    order = [("Yes", "Yes"), ("Yes", "No"), ("No", "Yes"), ("No", "No")]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{4cm}p{10.5cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    for rubric, rel in order:
        papers = tab.get((rubric, rel), [])
        label = f"Rubric={rubric}, Reliability={rel}"
        latex += f"{label} & {cite_keys(papers)} \\\\\n\\midrule\n"

    latex = latex.rstrip().removesuffix("\\midrule") + "\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Rubric Use and Reliability Reporting}
\label{tab:rubric-reliability-cite}
\end{table*}
"""
    return latex


# ---------------------------------------------------------------------------
# Table 3: Evaluation Dimension Coverage
# ---------------------------------------------------------------------------

def generate_table3_main(rows: list[dict]) -> str:
    dimensions = [
        ("Utility", "Utility"),
        ("Fidelity", "Fidelity"),
        ("Realism", "Realism"),
        ("Emotional Plausibility", "Emotional Plausibility"),
        ("Consistency", "Consistency"),
        ("Safety", "Safety"),
        ("Human Learning / Outcomes", "Human Learning / Outcomes"),
    ]
    total = len(rows)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lc}
\toprule
\textbf{Evaluation Dimension} & \textbf{Count (\%)} \\
\midrule
"""
    for label, col in dimensions:
        papers = yes_papers(rows, col)
        pct = len(papers) / total * 100
        latex += f"{label} & {len(papers)} ({pct:.1f}\\%) \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Evaluation Dimension Coverage Across Studies ($N=%d$)}
\label{tab:eval-dimensions}
\end{table*}
""" % total
    return latex


def generate_table3_cite(rows: list[dict]) -> str:
    dimensions = [
        ("Utility", "Utility"),
        ("Fidelity", "Fidelity"),
        ("Realism", "Realism"),
        ("Emotional Plausibility", "Emotional Plausibility"),
        ("Consistency", "Consistency"),
        ("Safety", "Safety"),
        ("Human Learning / Outcomes", "Human Learning / Outcomes"),
    ]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5cm}p{10cm}}
\toprule
\textbf{Evaluation Dimension} & \textbf{Papers} \\
\midrule
"""
    for label, col in dimensions:
        papers = yes_papers(rows, col)
        latex += f"{label} & {cite_keys(papers)} \\\\\n\\midrule\n"

    latex = latex.rstrip().removesuffix("\\midrule") + "\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Evaluation Dimension}
\label{tab:eval-dimensions-cite}
\end{table*}
"""
    return latex


# ---------------------------------------------------------------------------
# Table 4: Interaction Level × Behavioral Evaluation Depth
# ---------------------------------------------------------------------------

def generate_table4_main(rows: list[dict]) -> str:
    levels = ["Single-turn", "Short Multi-turn", "Extended Dialogue", "Longitudinal"]
    cols = ["Static", "Pattern-level", "Dynamic", "(unspecified)"]
    tab = _table4_data(rows)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lcccc}
\toprule
\textbf{Interaction Level} & \textbf{Static} & \textbf{Pattern-level} & \textbf{Dynamic} & \textbf{(unspecified)} \\
\midrule
"""
    for level in levels:
        cells = [str(len(tab.get((level, col), []))) for col in cols]
        latex += f"{level} & {' & '.join(cells)} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Interaction Level by Behavioral Evaluation Depth ($N=%d$)}
\label{tab:interaction-behavior}
\end{table*}
""" % len(rows)
    return latex


def generate_table4_cite(rows: list[dict]) -> str:
    levels = ["Single-turn", "Short Multi-turn", "Extended Dialogue", "Longitudinal"]
    cols = ["Static", "Pattern-level", "Dynamic", "(unspecified)"]
    tab = _table4_data(rows)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5.5cm}p{9.5cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    for level in levels:
        for col in cols:
            papers = tab.get((level, col), [])
            if papers:
                latex += f"{level} / {col} & {cite_keys(papers)} \\\\\n\\midrule\n"

    latex = latex.rstrip().removesuffix("\\midrule") + "\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Interaction Level and Behavioral Evaluation Depth}
\label{tab:interaction-behavior-cite}
\end{table*}
"""
    return latex


# ---------------------------------------------------------------------------
# Table 5: Human Learning × Lay Users × User Study
# ---------------------------------------------------------------------------

def generate_table5_main(rows: list[dict]) -> str:
    variables = [
        ("Human Learning / Outcomes", "Human Learning"),
        ("Eval_Lay_Users", "Lay Users"),
        ("Eval_User_Study", "User Study"),
    ]
    total = len(rows)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lcc}
\toprule
\textbf{Variable} & \textbf{Yes} & \textbf{No} \\
\midrule
"""
    for col, label in variables:
        yes_n = len(yes_papers(rows, col))
        no_n = total - yes_n
        latex += f"{label} & {yes_n} & {no_n} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Human-Facing Evaluation Coverage ($N=%d$)}
\label{tab:human-facing}
\end{table*}
""" % total
    return latex


def generate_table5_cite(rows: list[dict]) -> str:
    variables = [
        ("Human Learning / Outcomes", "Human Learning"),
        ("Eval_Lay_Users", "Lay Users"),
        ("Eval_User_Study", "User Study"),
    ]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{4cm}p{11cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    for col, label in variables:
        yes_list = yes_papers(rows, col)
        no_list = sorted(
            r["Citation_Key"] for r in rows
            if r.get(col, "").strip() == "No"
        )
        latex += f"{label} = Yes ({len(yes_list)}) & {cite_keys(yes_list)} \\\\\n\\midrule\n"
        latex += f"{label} = No ({len(no_list)}) & {cite_keys(no_list)} \\\\\n\\midrule\n"

    latex = latex.rstrip().removesuffix("\\midrule") + "\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Human-Facing Evaluation Variables}
\label{tab:human-facing-cite}
\end{table*}
"""
    return latex


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    csv_path = Path(__file__).parent.parent / "compare" / "final-table.csv"
    rows = read_data(str(csv_path))

    # Interleave: main table then citation table for each
    content = "% === Evaluation Methodology Tables ===\n\n"
    content += generate_table1_main(rows) + "\n"
    content += generate_table1_cite(rows) + "\n"
    content += generate_table2_main(rows) + "\n"
    content += generate_table2_cite(rows) + "\n"
    content += generate_table3_main(rows) + "\n"
    content += generate_table3_cite(rows) + "\n"
    content += generate_table4_main(rows) + "\n"
    content += generate_table4_cite(rows) + "\n"
    content += generate_table5_main(rows) + "\n"
    content += generate_table5_cite(rows)

    output_path = Path(__file__).parent / "eval_tables.tex"
    output_path.write_text(content)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
