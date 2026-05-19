#!/usr/bin/env python3
"""
Generate LaTeX tables from CSV data.

Usage:
    cd table
    uv run python generate_tables.py

Output:
    table/acl_latex_for_overleaf.tex - Ready to paste into ACL Overleaf project
"""

import pandas as pd
from pathlib import Path


def read_data(csv_path: str) -> pd.DataFrame:
    """Read CSV file and return DataFrame."""
    df = pd.read_csv(csv_path)
    return df


def generate_table1(df: pd.DataFrame) -> str:
    """Generate statistics table for Theory Grounding and Theory Operationalization."""
    # 处理缺失值：将NaN替换为"Not Specified"
    df_clean = df.copy()
    df_clean['Theory_Grounding'] = df_clean['Theory_Grounding'].fillna('Not Specified')
    df_clean['Theory_Operationalized_In_Evaluation'] = df_clean['Theory_Operationalized_In_Evaluation'].fillna('Not Specified')

    grounding_counts = df_clean["Theory_Grounding"].value_counts()
    grounding_total = len(df_clean)
    operational_counts = df_clean["Theory_Operationalized_In_Evaluation"].value_counts()
    operational_total = len(df_clean)

    # 动态获取所有分类
    all_categories = sorted(set(list(grounding_counts.index) + list(operational_counts.index)))

    latex = r"""\begin{table*}[tbp]
\centering
\begin{tabular}{l""" + "c" * (len(all_categories) + 1) + r"""}
\toprule
\textbf{Category}"""
    for cat in all_categories:
        latex += f" & \\textbf{{{cat}}}"
    latex += " & \\textbf{Total} \\\\\n\\midrule\n"

    # Theory Grounding行
    grounding_row = "Theory Grounding"
    for cat in all_categories:
        count = grounding_counts.get(cat, 0)
        if count > 0:
            pct = count / grounding_total * 100
            grounding_row += f" & {count} ({pct:.1f}\\%)"
        else:
            grounding_row += " & ---"
    grounding_row += f" & {grounding_total} \\\\"
    latex += grounding_row + "\n\\midrule\n"

    # Theory Operationalization行
    operational_row = "Theory Operationalization"
    for cat in all_categories:
        count = operational_counts.get(cat, 0)
        if count > 0:
            pct = count / operational_total * 100
            operational_row += f" & {count} ({pct:.1f}\\%)"
        else:
            operational_row += " & ---"
    operational_row += f" & {operational_total} \\\\"
    latex += operational_row + "\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Statistics of Theory Grounding and Theory Operationalization in Evaluation}
\label{tab:theory-stats}
\end{table*}
"""
    return latex


def generate_table2(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Grounding."""
    categories = ["Strong", "Partial", "Mentioned", "None", "Not Specified"]
    grouped = df.groupby("Theory_Grounding")["Citation_Key"].apply(list)

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
\caption{Papers Classified by Theory Grounding Level}
\label{tab:theory-grounding}
\end{table*}
"""
    return latex


def generate_table3(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Operationalization in Evaluation."""
    categories = ["Strong", "Partial", "Mentioned", "None", "Not Specified"]
    grouped = df.groupby("Theory_Operationalized_In_Evaluation")["Citation_Key"].apply(list)

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
\caption{Papers Classified by Theory Operationalization in Evaluation}
\label{tab:theory-operationalization}
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
\scriptsize
\renewcommand{\arraystretch}{0.75}
\begin{tabular}{p{4cm}p{3.2cm}p{6.8cm}}
\toprule
\textbf{What It Evaluates} & \textbf{Evaluation Type} & \textbf{Example Papers} \\
\midrule
"""

    items = list(type_papers.items())
    for i, (eval_type, papers) in enumerate(items):
        desc = descriptions.get(eval_type, "Other evaluation methods")
        papers_str = ", ".join([f"\\cite{{{p}}}" for p in papers])
        latex += f"{desc} & {eval_type} & {papers_str} \\\\\n"
        if i < len(items) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types}
\end{table*}
"""
    return latex


def main():
    """Main entry point."""
    csv_path = Path(__file__).parent / "theory_eval_refined_coding_refined.csv"
    df = read_data(csv_path)

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
