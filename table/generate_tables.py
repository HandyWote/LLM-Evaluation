#!/usr/bin/env python3
"""
Generate Theory LaTeX tables from theory_eval CSV.

Usage:
    cd table
    uv run python generate_tables.py

Output:
    table/acl_latex_for_overleaf.tex  - Theory tables (1-4)

NOTE: Evaluation methodology tables (eval_tables.tex) are owned by
generate_eval_tables.py, which reads compare/final-table.csv.
They are intentionally NOT generated here.
"""

import pandas as pd
from pathlib import Path


def read_data(csv_path: str) -> pd.DataFrame:
    """Read CSV file and return DataFrame, preserving 'N/A' strings."""
    df = pd.read_csv(csv_path, keep_default_na=False)
    return df


# ─── Theory Tables (1-4) ─────────────────────────────────────────


def generate_table1(df: pd.DataFrame) -> str:
    """Generate statistics table for Theory Grounding and Theory Operationalization."""
    df_clean = df.copy()
    df_clean['Theory_Grounding'] = df_clean['Theory_Grounding'].replace('', 'Not Specified')
    df_clean['Theory_Operationalized_In_Evaluation'] = df_clean['Theory_Operationalized_In_Evaluation'].replace('', 'Not Specified')

    grounding_counts = df_clean["Theory_Grounding"].value_counts()
    grounding_total = len(df_clean)
    operational_counts = df_clean["Theory_Operationalized_In_Evaluation"].value_counts()
    operational_total = len(df_clean)

    all_categories = ["Strong", "Partial", "Mentioned", "Not Specified"]
    active_categories = [cat for cat in all_categories
                        if grounding_counts.get(cat, 0) > 0 or operational_counts.get(cat, 0) > 0]

    latex = r"""\begin{table*}[tbp]
\centering
\begin{tabular}{l""" + "c" * (len(active_categories) + 1) + r"""}
\toprule
\textbf{Category}"""
    for cat in active_categories:
        latex += f" & \\textbf{{{cat}}}"
    latex += " & \\textbf{Total} \\\\\n\\midrule\n"

    grounding_row = "Theory Grounding"
    for cat in active_categories:
        count = grounding_counts.get(cat, 0)
        if count > 0:
            pct = count / grounding_total * 100
            grounding_row += f" & {count} ({pct:.1f}\\%)"
        else:
            grounding_row += " & ---"
    grounding_row += f" & {grounding_total} \\\\\n"
    latex += grounding_row + "\\midrule\n"

    operational_row = "Theory Operationalization"
    for cat in active_categories:
        count = operational_counts.get(cat, 0)
        if count > 0:
            pct = count / operational_total * 100
            operational_row += f" & {count} ({pct:.1f}\\%)"
        else:
            operational_row += " & ---"
    operational_row += f" & {operational_total} \\\\\n"
    latex += operational_row

    latex += r"""
\bottomrule
\end{tabular}
\caption{Statistics of Theory Grounding and Theory Operationalization in Evaluation}
\label{tab:theory-stats}
\end{table*}
"""
    return latex


def _generate_classification_table(df: pd.DataFrame, col: str, caption: str, label: str) -> str:
    """Generate a classification table for a given column."""
    categories = ["Strong", "Partial", "Mentioned", "None", "Not Specified"]
    grouped = df.groupby(col)["Citation_Key"].apply(list)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{2.5cm}p{12.4cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    first = True
    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            if not first:
                latex += "\\midrule\n"
            papers_str = ", ".join([f"\\cite{{{p}}}" for p in papers])
            latex += f"{cat} & {papers_str} \\\\\n"
            first = False

    latex += r"""\bottomrule
\end{tabular}
\caption{""" + caption + r"""}
\label{""" + label + r"""}
\end{table*}
"""
    return latex


def generate_table2(df: pd.DataFrame) -> str:
    return _generate_classification_table(df, "Theory_Grounding",
        "Papers Classified by Theory Grounding Level", "tab:theory-grounding")


def generate_table3(df: pd.DataFrame) -> str:
    return _generate_classification_table(df, "Theory_Operationalized_In_Evaluation",
        "Papers Classified by Theory Operationalization in Evaluation", "tab:theory-operationalization")


def generate_table4(df: pd.DataFrame) -> str:
    """Generate evaluation type analysis table."""
    eval_types = [
        "Validated scale",
        "Established therapy/counseling coding system",
        "Theory-specific rubric",
        "Custom expert rating",
        "Affective/emotional dynamics metric",
        "Clinical diagnostic benchmark",
        "Theory-specific benchmark/task",
        "LLM-based evaluation",
    ]

    type_papers = {}
    for eval_type in eval_types:
        mask = df["Theory_Eval_Type"].str.contains(eval_type, na=False, case=False)
        papers = df.loc[mask, "Citation_Key"].tolist()
        if papers:
            type_papers[eval_type] = papers

    descriptions = {
        "Validated scale": "Standardized psychological or clinical scales",
        "Established therapy/counseling coding system": "Therapy process or outcome coding",
        "Theory-specific rubric": "Custom rubrics based on theoretical constructs",
        "Custom expert rating": "Expert judgments on custom dimensions",
        "Affective/emotional dynamics metric": "Emotion recognition or affective computing metrics",
        "Clinical diagnostic benchmark": "Clinical diagnosis or screening benchmarks",
        "Theory-specific benchmark/task": "Task-specific performance benchmarks",
        "LLM-based evaluation": "LLM-generated ratings or judgments",
    }

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{6cm}p{8cm}}
\toprule
\textbf{Evaluation Type} & \textbf{Example Papers} \\
\midrule
"""
    items = list(type_papers.items())
    for i, (eval_type, papers) in enumerate(items):
        desc = descriptions.get(eval_type, "Other evaluation methods")
        papers_str = ", ".join([f"\\cite{{{p}}}" for p in papers])
        latex += f"{eval_type}\\newline\\textcolor{{gray}}{{\\footnotesize{{\\textit{{{desc}}}}}}} & {papers_str} \\\\\n"
        if i < len(items) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types}
\end{table*}
"""
    return latex


# ─── Main ─────────────────────────────────────────────────────────


def generate_theory_tables() -> str:
    """Generate Theory tables (1-4) from theory_eval CSV."""
    csv_path = Path(__file__).parent / "theory_eval_refined_coding_refined.csv"
    df = read_data(csv_path)

    content = "% === Theory Grounding & Operationalization Tables ===\n\n"
    content += generate_table1(df)
    content += "\n"
    content += generate_table2(df)
    content += "\n"
    content += generate_table3(df)
    content += "\n"
    content += generate_table4(df)
    return content


def main():
    """Main entry point."""
    theory_content = generate_theory_tables()
    theory_path = Path(__file__).parent / "acl_latex_for_overleaf.tex"
    theory_path.write_text(theory_content)
    print(f"Generated {theory_path}")


if __name__ == "__main__":
    main()
