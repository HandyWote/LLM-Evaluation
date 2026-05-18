#!/usr/bin/env python3
"""
Generate LaTeX tables from Excel data.

Usage:
    cd table
    uv run python generate_tables.py

Output:
    table/acl_latex_for_overleaf.tex - Ready to paste into ACL Overleaf project
"""

import pandas as pd
from pathlib import Path


def read_data(excel_path: str) -> pd.DataFrame:
    """Read Excel file and return DataFrame."""
    df = pd.read_excel(excel_path, sheet_name="theory_eval_refined_coding")
    return df


def generate_table1(df: pd.DataFrame) -> str:
    """Generate statistics table for Theory Grounding and Theory Operationalization."""
    grounding_counts = df["Theory_Grounding"].value_counts()
    grounding_total = len(df)
    operational_counts = df["Theory_Operationalized_In_Evaluation"].value_counts()
    operational_total = len(df)
    categories = ["Strong", "Partial", "Mentioned", "None"]

    latex = r"""\begin{table*}[tbp]
\centering
\caption{Statistics of Theory Grounding and Theory Operationalization in Evaluation}
\label{tab:theory-stats}
\begin{tabular}{lccccc}
\toprule
\textbf{Category} & \textbf{Strong} & \textbf{Partial} & \textbf{Mentioned} & \textbf{None} & \textbf{Total} \\
\midrule
"""

    grounding_row = "Theory Grounding"
    for cat in categories:
        count = grounding_counts.get(cat, 0)
        pct = count / grounding_total * 100
        grounding_row += f" & {count} ({pct:.1f}\\%)"
    grounding_row += f" & {grounding_total} \\\\"
    latex += grounding_row + "\n\\midrule\n"

    operational_row = "Theory Operationalization"
    for cat in categories:
        count = operational_counts.get(cat, 0)
        pct = count / operational_total * 100
        operational_row += f" & {count} ({pct:.1f}\\%)"
    operational_row += f" & {operational_total} \\\\"
    latex += operational_row + "\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table*}
"""
    return latex


def generate_table2(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Grounding."""
    categories = ["Strong", "Partial", "Mentioned", "None"]
    grouped = df.groupby("Theory_Grounding")["Citation_Key"].apply(list)

    latex = r"""\begin{table*}[tbp]
\centering
\caption{Papers Classified by Theory Grounding Level}
\label{tab:theory-grounding}
\small
\begin{tabular}{p{2.5cm}p{12.4cm}}
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
"""

    for i, cat in enumerate(categories):
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"
        if i < len(categories) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table*}
"""
    return latex


def generate_table3(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Operationalization in Evaluation."""
    categories = ["Strong", "Partial", "Mentioned", "None"]
    grouped = df.groupby("Theory_Operationalized_In_Evaluation")["Citation_Key"].apply(list)

    latex = r"""\begin{table*}[tbp]
\centering
\caption{Papers Classified by Theory Operationalization in Evaluation}
\label{tab:theory-operationalization}
\small
\begin{tabular}{p{2.5cm}p{12.4cm}}
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
"""

    for i, cat in enumerate(categories):
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"
        if i < len(categories) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table*}
"""
    return latex


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
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types}
\scriptsize
\renewcommand{\arraystretch}{0.75}
\begin{tabular}{p{3.2cm}p{4cm}p{6.8cm}}
\toprule
\textbf{Evaluation Type} & \textbf{What It Evaluates} & \textbf{Example Papers} \\
\midrule
"""

    items = list(type_papers.items())
    for i, (eval_type, papers) in enumerate(items):
        desc = descriptions.get(eval_type, "Other evaluation methods")
        papers_str = ", ".join(papers)
        latex += f"{eval_type} & {desc} & {papers_str} \\\\\n"
        if i < len(items) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table*}
"""
    return latex


def main():
    """Main entry point."""
    excel_path = Path(__file__).parent / "theory_eval_refined_coding_refined.xlsx"
    df = read_data(excel_path)

    content = r"""% === Theory Grounding & Operationalization Tables ===

"""

    content += generate_table1(df)
    content += "\n"
    content += generate_table2(df)
    content += "\n"
    content += generate_table3(df)
    content += "\n"
    content += generate_table4(df)

    output_path = Path(__file__).parent / "acl_latex_for_overleaf.tex"
    output_path.write_text(content)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
